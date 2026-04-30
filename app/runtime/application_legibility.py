from __future__ import annotations

from pathlib import Path

from app.core.context_compressor import summarize_paths, summarize_text
from app.core.models import ReaderSpec
from app.core.schema_validator import SchemaValidator
from app.runtime.artifact_readers import (
    ArtifactReaderRegistry,
    BrowserPreviewReader,
    LogArtifactReader,
    MetricArtifactReader,
)
MAX_ARTIFACTS_PER_KIND = 4
MAX_PATH_SUMMARY_CHARS = 320


class ApplicationLegibilityCollector:
    def __init__(self, reader_registry: ArtifactReaderRegistry | None = None) -> None:
        self.reader_registry = reader_registry or build_default_reader_registry()

    def collect(self, repo_path: Path) -> dict[str, object]:
        reader_results = self.reader_registry.read_all(repo_path)
        preview_targets = self._paths_for_kind(reader_results, "preview")
        log_files = self._paths_for_kind(reader_results, "log")
        metric_files = self._paths_for_kind(reader_results, "metric")
        artifact_summaries = self._artifact_summaries(reader_results)
        return {
            "available": bool(preview_targets or log_files or metric_files),
            "reader_results": reader_results,
            "preview_targets": preview_targets,
            "preview_targets_summary": summarize_paths(
                preview_targets,
                max_items=MAX_ARTIFACTS_PER_KIND,
                max_chars=MAX_PATH_SUMMARY_CHARS,
            ),
            "log_files": log_files,
            "log_files_summary": summarize_paths(
                log_files,
                max_items=MAX_ARTIFACTS_PER_KIND,
                max_chars=MAX_PATH_SUMMARY_CHARS,
            ),
            "metric_files": metric_files,
            "metric_files_summary": summarize_paths(
                metric_files,
                max_items=MAX_ARTIFACTS_PER_KIND,
                max_chars=MAX_PATH_SUMMARY_CHARS,
            ),
            "artifact_summaries": artifact_summaries,
        }

    def _paths_for_kind(self, reader_results: list[dict], artifact_kind: str) -> list[str]:
        for item in reader_results:
            if item.get("artifact_kind") == artifact_kind:
                paths = item.get("paths", [])
                return list(paths) if isinstance(paths, list) else []
        return []

    def _artifact_summaries(self, reader_results: list[dict]) -> list[dict[str, str]]:
        summaries: list[dict[str, str]] = []
        for item in reader_results:
            artifacts = item.get("artifacts", [])
            if not isinstance(artifacts, list):
                continue
            for artifact in artifacts[:MAX_ARTIFACTS_PER_KIND]:
                if isinstance(artifact, dict):
                    summaries.append(
                        {
                            "kind": str(artifact.get("kind", "")),
                            "path": str(artifact.get("path", "")),
                            "summary": summarize_text(str(artifact.get("summary", "")), max_chars=MAX_PATH_SUMMARY_CHARS),
                        }
                    )
        return summaries


def build_default_reader_registry() -> ArtifactReaderRegistry:
    reader_specs = [
        ReaderSpec(
            name="browser_preview",
            artifact_kind="preview",
            description="Collect browser-openable preview html artifacts.",
            output_schema={"reader": "string", "artifact_kind": "string", "paths": "list", "summary": "string", "artifacts": "list"},
        ),
        ReaderSpec(
            name="log_artifact",
            artifact_kind="log",
            description="Collect runtime and harness log artifacts.",
            output_schema={"reader": "string", "artifact_kind": "string", "paths": "list", "summary": "string", "artifacts": "list"},
        ),
        ReaderSpec(
            name="metric_artifact",
            artifact_kind="metric",
            description="Collect coverage and metric report artifacts.",
            output_schema={"reader": "string", "artifact_kind": "string", "paths": "list", "summary": "string", "artifacts": "list"},
        ),
    ]
    registry = ArtifactReaderRegistry(reader_specs, validator=SchemaValidator())
    registry.register(BrowserPreviewReader())
    registry.register(LogArtifactReader())
    registry.register(MetricArtifactReader())
    return registry
