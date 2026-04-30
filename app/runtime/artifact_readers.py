from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from app.core.context_compressor import summarize_paths, summarize_text
from app.core.models import ReaderSpec
from app.core.schema_validator import SchemaValidator


MAX_ARTIFACTS_PER_READER = 4
MAX_ARTIFACT_SUMMARY_CHARS = 240
MAX_PATH_SUMMARY_CHARS = 320


class BaseArtifactReader(ABC):
    name: str
    artifact_kind: str

    @abstractmethod
    def read(self, repo_path: Path) -> dict:
        raise NotImplementedError


class BrowserPreviewReader(BaseArtifactReader):
    name = "browser_preview"
    artifact_kind = "preview"

    def read(self, repo_path: Path) -> dict:
        paths = self._collect_paths(repo_path, allowed_dir_names=("examples", "example", "demo", "demos", "preview", "previews"))
        return _build_reader_result(repo_path, self.name, self.artifact_kind, paths)

    def _collect_paths(self, repo_path: Path, *, allowed_dir_names: tuple[str, ...]) -> list[str]:
        collected: list[str] = []
        for path in sorted(repo_path.rglob("*")):
            if len(collected) >= MAX_ARTIFACTS_PER_READER:
                break
            if not path.is_file() or path.suffix.lower() != ".html":
                continue
            relative_path = path.relative_to(repo_path)
            if any(part in allowed_dir_names for part in relative_path.parts[:-1]):
                collected.append(str(relative_path))
        return collected


class LogArtifactReader(BaseArtifactReader):
    name = "log_artifact"
    artifact_kind = "log"

    def read(self, repo_path: Path) -> dict:
        paths = self._collect_paths(repo_path, allowed_dir_names=("logs", ".claude-code"))
        return _build_reader_result(repo_path, self.name, self.artifact_kind, paths)

    def _collect_paths(self, repo_path: Path, *, allowed_dir_names: tuple[str, ...]) -> list[str]:
        collected: list[str] = []
        for path in sorted(repo_path.rglob("*")):
            if len(collected) >= MAX_ARTIFACTS_PER_READER:
                break
            if not path.is_file() or path.suffix.lower() not in {".log", ".out", ".txt"}:
                continue
            relative_path = path.relative_to(repo_path)
            if any(part in allowed_dir_names for part in relative_path.parts[:-1]):
                collected.append(str(relative_path))
        return collected


class MetricArtifactReader(BaseArtifactReader):
    name = "metric_artifact"
    artifact_kind = "metric"

    def read(self, repo_path: Path) -> dict:
        paths = self._collect_paths(repo_path, allowed_dir_names=("reports", "report", "metrics", ".claude-code"))
        return _build_reader_result(repo_path, self.name, self.artifact_kind, paths)

    def _collect_paths(self, repo_path: Path, *, allowed_dir_names: tuple[str, ...]) -> list[str]:
        collected: list[str] = []
        allowed_names = {"coverage.xml", "coverage.json"}
        for path in sorted(repo_path.rglob("*")):
            if len(collected) >= MAX_ARTIFACTS_PER_READER:
                break
            if not path.is_file():
                continue
            if path.name not in allowed_names and path.suffix.lower() not in {".json", ".xml"}:
                continue
            relative_path = path.relative_to(repo_path)
            if any(part in allowed_dir_names for part in relative_path.parts[:-1]):
                collected.append(str(relative_path))
        return collected


class ArtifactReaderRegistry:
    def __init__(self, reader_specs: list[ReaderSpec], validator: SchemaValidator | None = None) -> None:
        self.validator = validator or SchemaValidator()
        self.specs = {spec.name: spec for spec in reader_specs}
        self.readers: dict[str, BaseArtifactReader] = {}

    def register(self, reader: BaseArtifactReader) -> None:
        if reader.name not in self.specs:
            raise KeyError(f"unknown reader spec: {reader.name}")
        self.readers[reader.name] = reader

    def read_all(self, repo_path: Path) -> list[dict]:
        results: list[dict] = []
        for name in sorted(self.readers):
            spec = self.specs[name]
            result = self.readers[name].read(repo_path)
            errors = self.validator.validate_schema(result, spec.output_schema, label=f"{name} output")
            if errors:
                raise ValueError("; ".join(errors))
            results.append(result)
        return results

    def describe_many(self, names: list[str]) -> list[dict[str, str]]:
        descriptions: list[dict[str, str]] = []
        for name in names:
            spec = self.specs.get(name)
            if spec is None:
                continue
            descriptions.append(
                {
                    "name": spec.name,
                    "artifact_kind": spec.artifact_kind,
                    "description": spec.description,
                }
            )
        return descriptions


def _build_reader_result(repo_path: Path, reader_name: str, artifact_kind: str, paths: list[str]) -> dict:
    artifacts = []
    for relative_path in paths:
        file_path = repo_path / relative_path
        try:
            text = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        artifacts.append(
            {
                "kind": artifact_kind,
                "path": relative_path,
                "summary": summarize_text(text, max_chars=MAX_ARTIFACT_SUMMARY_CHARS),
            }
        )
    return {
        "reader": reader_name,
        "artifact_kind": artifact_kind,
        "paths": paths,
        "summary": summarize_paths(paths, max_items=MAX_ARTIFACTS_PER_READER, max_chars=MAX_PATH_SUMMARY_CHARS),
        "artifacts": artifacts,
    }
