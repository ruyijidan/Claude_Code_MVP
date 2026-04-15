from __future__ import annotations

from pathlib import Path

from app.agents.coder_agent import CoderAgent
from app.agents.critic_agent import CriticAgent
from app.agents.router_agent import RouterAgent
from app.agents.verifier_agent import VerifierAgent
from app.agent.completion_contracts import CompletionContractRegistry
from app.agent.context_builder import RepoContextBuilder
from app.agent.planner import LightweightPlanner
from app.agent.verification_gates import VerificationGateRunner
from app.core.memory_store import MemoryStore
from app.core.spec_loader import SpecLoader
from app.evals.evaluator import Evaluator
from app.evals.replay import ReplayLogger
from app.runtime.ecc_adapter import ECCAdapter
from app.superpowers.failure_classifier import FailureClassifier
from app.superpowers.repair_policy import RepairPolicy
from app.superpowers.retry_policy import RetryPolicy
from app.superpowers.self_repair import SelfRepairEngine


class CodingAgentLoop:
    def __init__(
        self,
        spec_loader: SpecLoader,
        memory_store: MemoryStore,
        adapter: ECCAdapter,
    ) -> None:
        self.spec_loader = spec_loader
        self.memory_store = memory_store
        self.adapter = adapter
        self.context_builder = RepoContextBuilder(adapter)
        self.planner = LightweightPlanner()
        self.completion_contracts = CompletionContractRegistry()
        self.gate_runner = VerificationGateRunner(self.completion_contracts)
        self.failure_classifier = FailureClassifier()
        self.repair_policy = RepairPolicy()
        self.retry_policy = RetryPolicy()
        self.repair_engine = SelfRepairEngine(adapter)
        self.evaluator = Evaluator()
        self.replay_logger = ReplayLogger(memory_store)

    def run(self, repo_path: Path, prompt: str, task_name: str | None = None) -> dict:
        task_type = task_name or self.planner.infer_task_type(prompt)
        task_spec = self.spec_loader.load_task(task_type)
        workflow_name = self.planner.workflow_name_for_task_type(task_type)
        workflow_spec = self.spec_loader.load_workflow(workflow_name)
        context = self.context_builder.build(repo_path, prompt)
        plan = self.planner.build_plan(prompt, context, task_type, workflow_spec)
        provider_info = self.adapter.provider_info()

        state = {
            "repo_path": repo_path,
            "request": {
                "repo_path": str(repo_path),
                "feature_request": prompt,
            },
            "task_spec": task_spec,
            "workflow_spec": workflow_spec,
            "runtime_provider": self.adapter.provider_name,
            "provider_info": provider_info,
            "repo_context": context,
            "plan": plan,
        }

        coder = CoderAgent(self.spec_loader.load_agent("coder"), self.adapter)
        verifier = VerifierAgent(self.spec_loader.load_agent("verifier"), self.adapter)
        critic = CriticAgent(
            self.spec_loader.load_agent("critic"),
            self.spec_loader.load_rule("surgical-changes"),
        )
        router = RouterAgent(self.spec_loader.load_agent("router"))

        state.update(coder.run(state))
        state.update(verifier.run(state))
        state.update(self.gate_runner.run_post_execute(state))
        state.update(critic.run(state))
        state.update(router.run(state))

        attempt = 1
        repair_attempts: list[dict] = []
        state.update(self._record_repair_state(state, attempt, repair_attempts))
        while state.get("critic_issues"):
            decision = self.repair_policy.decide(
                attempt,
                self.failure_classifier.classify(state, state.get("critic_issues", [])),
                workflow_spec,
            )
            retry_allowed = decision.retry_allowed and self.retry_policy.should_retry(attempt, state.get("critic_issues", []))
            repair_attempt = {
                "attempt": attempt,
                "failure_signals": [item.to_dict() for item in self.failure_classifier.classify(state, state.get("critic_issues", []))],
                "repair_decision": decision.to_dict(),
                "retry_allowed": retry_allowed,
            }
            repair_attempts.append(repair_attempt)
            state.update(
                {
                    "failure_signals": repair_attempt["failure_signals"],
                    "repair_decision": repair_attempt["repair_decision"],
                    "repair_attempts": list(repair_attempts),
                }
            )
            if not retry_allowed:
                break
            state.update(self.repair_engine.repair(state, decision))
            state.update(verifier.run(state))
            state.update(self.gate_runner.run_post_execute(state))
            state.update(critic.run(state))
            state.update(router.run(state))
            attempt += 1

        state.update(self.evaluator.score(state))
        state["trajectory_path"] = self.replay_logger.persist(state)
        return state

    def _record_repair_state(self, state: dict, attempt: int, repair_attempts: list[dict]) -> dict:
        failure_signals = self.failure_classifier.classify(state, state.get("critic_issues", []))
        repair_decision = self.repair_policy.decide(attempt, failure_signals, state.get("workflow_spec"))
        return {
            "failure_signals": [item.to_dict() for item in failure_signals],
            "repair_decision": repair_decision.to_dict(),
            "repair_attempts": list(repair_attempts),
        }
