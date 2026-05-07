from __future__ import annotations

from pathlib import Path

from app.agents.coder_agent import CoderAgent
from app.agents.critic_agent import CriticAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.router_agent import RouterAgent
from app.agents.verifier_agent import VerifierAgent
from app.agent.completion_contracts import CompletionContractRegistry
from app.agent.context_builder import RepoContextBuilder
from app.agent.orchestrator import AgentOrchestrator
from app.agent.policies import PermissionPipeline, make_file_write_guard
from app.agent.planner import LightweightPlanner
from app.agent.workflow_executor import WorkflowExecutor
from app.agent.verification_gates import VerificationGateRunner
from app.core.memory_store import MemoryStore
from app.core.spec_loader import SpecLoader
from app.core.tool_registry import ToolRegistry
from app.evals.evaluator import Evaluator
from app.evals.replay import ReplayLogger
from app.runtime.application_legibility import ApplicationLegibilityCollector
from app.runtime.artifact_readers import ArtifactReaderRegistry, BrowserPreviewReader, LogArtifactReader, MetricArtifactReader
from app.runtime.ecc_adapter import ECCAdapter
from app.superpowers.failure_classifier import FailureClassifier
from app.superpowers.repair_policy import RepairPolicy
from app.superpowers.retry_policy import RetryPolicy
from app.superpowers.self_repair import SelfRepairEngine
from app.tools.file_tool import FileTool
from app.tools.test_tool import TestTool


class CodingAgentLoop:
    def __init__(
        self,
        spec_loader: SpecLoader,
        memory_store: MemoryStore,
        adapter: ECCAdapter,
        permission_pipeline: PermissionPipeline | None = None,
    ) -> None:
        self.spec_loader = spec_loader
        self.memory_store = memory_store
        self.adapter = adapter
        self.permission_pipeline = permission_pipeline or PermissionPipeline()
        self.tool_registry = self._build_tool_registry()
        self.reader_registry = self._build_reader_registry()
        self.context_builder = RepoContextBuilder(
            adapter,
            legibility_collector=ApplicationLegibilityCollector(self.reader_registry),
            memory_store=self.memory_store,
        )
        self.planner = LightweightPlanner()
        self.orchestrator = AgentOrchestrator()
        self.workflow_executor = WorkflowExecutor(self.tool_registry, self.reader_registry)
        self.completion_contracts = CompletionContractRegistry()
        self.gate_runner = VerificationGateRunner(self.completion_contracts)
        self.failure_classifier = FailureClassifier()
        self.repair_policy = RepairPolicy()
        self.retry_policy = RetryPolicy()
        self.repair_engine = SelfRepairEngine(adapter)
        self.evaluator = Evaluator()
        self.replay_logger = ReplayLogger(memory_store)

    def run(self, repo_path: Path, prompt: str, task_name: str | None = None) -> dict:
        self.orchestrator = AgentOrchestrator()
        if self.adapter.file_guard is None:
            self.adapter.configure_file_guard(make_file_write_guard(self.permission_pipeline, repo_root=repo_path))
        workflows = self.spec_loader.load_workflows()
        task_type = task_name or self.planner.infer_task_type(prompt, workflows)
        task_spec = self.spec_loader.load_task(task_type)
        workflow_name = self.planner.workflow_name_for_task_type(task_type, workflows)
        workflow_spec = self.spec_loader.load_workflow(workflow_name)
        context = self.context_builder.build(repo_path, prompt, task_name=task_type)
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
        state["workflow_execution"] = self.workflow_executor.begin(task_spec, workflow_spec, context, plan)
        state["agent_transitions"] = []

        planner_spec = self.spec_loader.load_agent("planner")
        coder_spec = self.spec_loader.load_agent("coder")
        verifier_spec = self.spec_loader.load_agent("verifier")
        critic_spec = self.spec_loader.load_agent("critic")
        router_spec = self.spec_loader.load_agent("router")

        planner_agent = PlannerAgent(planner_spec)
        coder = CoderAgent(coder_spec, self.adapter)
        verifier = VerifierAgent(
            verifier_spec,
            self.adapter,
            self.tool_registry,
            self.spec_loader.load_rules(),
        )
        critic = CriticAgent(
            critic_spec,
            self.spec_loader.load_rules(),
        )
        router = RouterAgent(router_spec)

        planner_result = planner_agent.run(self.orchestrator.isolated_state(planner_spec, state))
        self.orchestrator.record_transition(planner_spec, state, planner_result, status="completed", next_agent="coder")
        state.update(planner_result)
        coder_result = coder.run(self.orchestrator.isolated_state(coder_spec, state))
        self.orchestrator.record_transition(coder_spec, state, coder_result, status="completed", next_agent="verifier")
        state.update(coder_result)
        verifier_result = verifier.run(self.orchestrator.isolated_state(verifier_spec, state))
        self.orchestrator.record_transition(verifier_spec, state, verifier_result, status="completed", next_agent="critic")
        state.update(verifier_result)
        state.update(self.gate_runner.run_post_execute(state))
        critic_result = critic.run(self.orchestrator.isolated_state(critic_spec, state))
        self.orchestrator.record_transition(critic_spec, state, critic_result, status="completed", next_agent="router")
        state.update(critic_result)
        router_result = router.run(self.orchestrator.isolated_state(router_spec, state))
        self.orchestrator.record_transition(router_spec, state, router_result, status="completed")
        state.update(router_result)
        state.update(self.workflow_executor.complete(state))
        state["agent_transitions"] = self.orchestrator.history()

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
            verifier_result = verifier.run(self.orchestrator.isolated_state(verifier_spec, state))
            self.orchestrator.record_transition(verifier_spec, state, verifier_result, status="repair_verification", next_agent="critic")
            state.update(verifier_result)
            state.update(self.gate_runner.run_post_execute(state))
            critic_result = critic.run(self.orchestrator.isolated_state(critic_spec, state))
            self.orchestrator.record_transition(critic_spec, state, critic_result, status="repair_critique", next_agent="router")
            state.update(critic_result)
            router_result = router.run(self.orchestrator.isolated_state(router_spec, state))
            self.orchestrator.record_transition(router_spec, state, router_result, status="repair_routing")
            state.update(router_result)
            state.update(self.workflow_executor.complete(state))
            state["agent_transitions"] = self.orchestrator.history()
            attempt += 1

        state.update(self.evaluator.score(state))
        state["agent_transitions"] = self.orchestrator.history()
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

    def _build_tool_registry(self) -> ToolRegistry:
        registry = ToolRegistry(self.spec_loader.load_tools())
        registry.register(FileTool())
        registry.register(TestTool(self.adapter))
        return registry

    def _build_reader_registry(self) -> ArtifactReaderRegistry:
        registry = ArtifactReaderRegistry(self.spec_loader.load_readers())
        registry.register(BrowserPreviewReader())
        registry.register(LogArtifactReader())
        registry.register(MetricArtifactReader())
        return registry
