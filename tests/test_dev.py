"""
Tests for the `token-count` and `compare` subcommands in scripts/dev.py.

Tests drive the CLI as a subprocess to exercise the real argument-parsing
layer and exit-code semantics.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

# Absolute path to the script under test so tests work regardless of cwd.
_DEV_SCRIPT = str(Path(__file__).resolve().parents[1] / "scripts" / "dev.py")

# A real file that exists in the repo and has known non-zero content.
_SPEC_FILE = str(Path(__file__).resolve().parents[1] / "specs" / "001-token-cli" / "spec.md")


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    """Run `python scripts/dev.py <args>` and return the completed process."""
    return subprocess.run(
        [sys.executable, _DEV_SCRIPT, *args],
        capture_output=True,
        text=True,
    )


class TokenCountTests(unittest.TestCase):
    # ------------------------------------------------------------------
    # Scenario 1: single file
    # ------------------------------------------------------------------
    def test_single_file_shows_filename_and_token_count(self) -> None:
        """Output must contain the filename and a numeric token count."""
        result = _run("token-count", _SPEC_FILE)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        output = result.stdout

        # Filename (basename is fine; full path also acceptable)
        self.assertIn("spec.md", output)

        # At least one token count number must appear
        numbers = [token for token in output.split() if token.isdigit()]
        self.assertTrue(
            len(numbers) >= 1,
            msg=f"Expected a numeric token count in output, got:\n{output}",
        )

    # ------------------------------------------------------------------
    # Scenario 2: multiple files → per-file counts + total row
    # ------------------------------------------------------------------
    def test_multiple_files_shows_each_count_and_total(self) -> None:
        """Each filename must appear with its count; a 'total' row must follow."""
        with tempfile.TemporaryDirectory() as tmp:
            file_a = Path(tmp) / "a.txt"
            file_b = Path(tmp) / "b.txt"
            file_a.write_text("hello world", encoding="utf-8")
            file_b.write_text("foo bar baz", encoding="utf-8")

            result = _run("token-count", str(file_a), str(file_b))

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        output = result.stdout.lower()

        self.assertIn("a.txt", output)
        self.assertIn("b.txt", output)
        self.assertIn("total", output)

    # ------------------------------------------------------------------
    # Scenario 3: non-existent file → non-zero exit + filename in error
    # ------------------------------------------------------------------
    def test_nonexistent_file_exits_nonzero_with_filename_in_error(self) -> None:
        """A missing file must cause a non-zero exit; the filename must appear
        in stderr (or stdout — whichever the implementation chooses)."""
        nonexistent = str(
            Path(tempfile.gettempdir()) / f"nonexistent-{uuid.uuid4().hex}.md"
        )
        result = _run("token-count", nonexistent)

        self.assertNotEqual(result.returncode, 0, msg="Expected non-zero exit for missing file")
        combined = result.stdout + result.stderr
        self.assertIn(Path(nonexistent).name, combined)

    # ------------------------------------------------------------------
    # Edge case 4: empty file → 0 tokens, exit 0
    # ------------------------------------------------------------------
    def test_empty_file_outputs_zero_tokens_and_exits_successfully(self) -> None:
        """An empty file should report 0 tokens and exit cleanly."""
        with tempfile.NamedTemporaryFile(
            suffix=".tmp", delete=False, mode="w", encoding="utf-8"
        ) as fh:
            tmp_path = fh.name
            # write nothing

        try:
            result = _run("token-count", tmp_path)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        output = result.stdout
        self.assertIn("0", output)


class CompareTests(unittest.TestCase):
    # ------------------------------------------------------------------
    # Scenario 1: two files with different content → diff + percentage
    # ------------------------------------------------------------------
    def test_compare_shows_both_filenames_diff_and_percentage(self) -> None:
        """Output must include both filenames, an absolute diff, and a '%' sign."""
        with tempfile.TemporaryDirectory() as tmp:
            baseline = Path(tmp) / "baseline.txt"
            target = Path(tmp) / "target.txt"
            baseline.write_text("hello world", encoding="utf-8")
            target.write_text(
                "the quick brown fox jumps over the lazy dog", encoding="utf-8"
            )

            result = _run("compare", str(baseline), str(target))

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        output = result.stdout

        self.assertIn("baseline.txt", output)
        self.assertIn("target.txt", output)
        self.assertIn("%", output)

    # ------------------------------------------------------------------
    # Scenario 2: equal files → diff is 0
    # ------------------------------------------------------------------
    def test_compare_equal_files_shows_zero_diff(self) -> None:
        """When both files have identical content the diff must be 0."""
        with tempfile.TemporaryDirectory() as tmp:
            file_a = Path(tmp) / "a.txt"
            file_b = Path(tmp) / "b.txt"
            file_a.write_text("same content here", encoding="utf-8")
            file_b.write_text("same content here", encoding="utf-8")

            result = _run("compare", str(file_a), str(file_b))

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        output = result.stdout
        self.assertIn("0", output)
        self.assertIn("%", output)

    # ------------------------------------------------------------------
    # Scenario 3: missing file → non-zero exit + filename in error
    # ------------------------------------------------------------------
    def test_compare_missing_file_exits_nonzero_with_filename_in_error(self) -> None:
        """A missing baseline must cause a non-zero exit with the filename in output."""
        nonexistent = str(
            Path(tempfile.gettempdir()) / f"nonexistent-{uuid.uuid4().hex}.txt"
        )
        with tempfile.NamedTemporaryFile(
            suffix=".txt", delete=False, mode="w", encoding="utf-8"
        ) as fh:
            real_file = fh.name
            fh.write("some content")

        try:
            result = _run("compare", nonexistent, real_file)
        finally:
            Path(real_file).unlink(missing_ok=True)

        self.assertNotEqual(result.returncode, 0)
        combined = result.stdout + result.stderr
        self.assertIn(Path(nonexistent).name, combined)

    # ------------------------------------------------------------------
    # Scenario 4: too few args → argparse error, non-zero exit (FR-007)
    # ------------------------------------------------------------------
    def test_compare_too_few_args_exits_nonzero(self) -> None:
        """Passing only one file to compare must exit non-zero."""
        result = _run("compare", _SPEC_FILE)
        self.assertNotEqual(result.returncode, 0)

    # ------------------------------------------------------------------
    # Scenario 5: too many args → argparse error, non-zero exit (FR-007)
    # ------------------------------------------------------------------
    def test_compare_too_many_args_exits_nonzero(self) -> None:
        """Passing three files to compare must exit non-zero."""
        result = _run("compare", _SPEC_FILE, _SPEC_FILE, _SPEC_FILE)
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
