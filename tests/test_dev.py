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


class WordCountTests(unittest.TestCase):
    # ------------------------------------------------------------------
    # Scenario 1: single file → filename + word count, exit 0
    # ------------------------------------------------------------------
    def test_single_file_shows_filename_and_word_count(self) -> None:
        """Output must contain the filename and the correct word count."""
        with tempfile.NamedTemporaryFile(
            suffix=".txt", delete=False, mode="w", encoding="utf-8"
        ) as fh:
            tmp_path = fh.name
            fh.write("hello world foo")

        try:
            result = _run("word-count", tmp_path)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        output = result.stdout
        self.assertIn(Path(tmp_path).name, output)
        self.assertIn("3", output)

    # ------------------------------------------------------------------
    # Scenario 2: multiple files → per-file counts + separator + total
    # ------------------------------------------------------------------
    def test_multiple_files_shows_each_count_and_total(self) -> None:
        """Each filename must appear with its count; a 'total' row must follow."""
        with tempfile.TemporaryDirectory() as tmp:
            file_a = Path(tmp) / "alpha.txt"
            file_b = Path(tmp) / "beta.txt"
            file_a.write_text("one two", encoding="utf-8")
            file_b.write_text("foo bar", encoding="utf-8")

            result = _run("word-count", str(file_a), str(file_b))

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        output = result.stdout.lower()

        self.assertIn("alpha.txt", output)
        self.assertIn("beta.txt", output)
        self.assertIn("total", output)
        self.assertIn("4", output)

    # ------------------------------------------------------------------
    # Scenario 3: empty file → 0 words, exit 0
    # ------------------------------------------------------------------
    def test_empty_file_outputs_zero_and_exits_successfully(self) -> None:
        """An empty file should report 0 words and exit cleanly."""
        with tempfile.NamedTemporaryFile(
            suffix=".txt", delete=False, mode="w", encoding="utf-8"
        ) as fh:
            tmp_path = fh.name
            # write nothing

        try:
            result = _run("word-count", tmp_path)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("0", result.stdout)

    # ------------------------------------------------------------------
    # Scenario 4: whitespace-only file → 0 words, exit 0
    # ------------------------------------------------------------------
    def test_whitespace_only_file_outputs_zero(self) -> None:
        """A file containing only spaces and newlines should report 0 words."""
        with tempfile.NamedTemporaryFile(
            suffix=".txt", delete=False, mode="w", encoding="utf-8"
        ) as fh:
            tmp_path = fh.name
            fh.write("   \n\t\n  ")

        try:
            result = _run("word-count", tmp_path)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("0", result.stdout)

    # ------------------------------------------------------------------
    # Scenario 5: non-existent file → stderr has error info, exit 1
    # ------------------------------------------------------------------
    def test_nonexistent_file_exits_nonzero_with_error_in_stderr(self) -> None:
        """A missing file must cause a non-zero exit with an error in stderr."""
        nonexistent = str(
            Path(tempfile.gettempdir()) / f"nonexistent-{uuid.uuid4().hex}.txt"
        )
        result = _run("word-count", nonexistent)

        self.assertNotEqual(result.returncode, 0, msg="Expected non-zero exit for missing file")
        self.assertTrue(
            result.stderr.strip(),
            msg="Expected error output in stderr for missing file",
        )


class ScanTests(unittest.TestCase):
    # ------------------------------------------------------------------
    # T008 — User Story 1: basic directory scan
    # ------------------------------------------------------------------

    def test_multi_file_dir_sorted_by_tokens_descending(self) -> None:
        """Scan a directory with 2+ files; output must have header, one row per
        file sorted token-descending, a total row, and exit 0."""
        with tempfile.TemporaryDirectory() as tmp:
            small = Path(tmp) / "small.txt"
            large = Path(tmp) / "large.txt"
            small.write_text("hi", encoding="utf-8")
            large.write_text(
                "the quick brown fox jumps over the lazy dog " * 20,
                encoding="utf-8",
            )

            result = _run("scan", tmp)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        output = result.stdout
        output_lower = output.lower()

        # Header row
        self.assertIn("file", output_lower)
        self.assertIn("token", output_lower)
        self.assertIn("word", output_lower)

        # Both files appear
        self.assertIn("small.txt", output)
        self.assertIn("large.txt", output)

        # Total row present (contains file count)
        self.assertIn("total", output_lower)

        # large.txt must appear before small.txt (higher token count first)
        self.assertLess(
            output.index("large.txt"),
            output.index("small.txt"),
            msg="large.txt (more tokens) should appear before small.txt",
        )

    def test_empty_directory_reports_no_files_found(self) -> None:
        """An empty directory must report 'no files found' and exit 0."""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run("scan", tmp)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("no files found", result.stdout.lower())

    def test_nonexistent_directory_exits_nonzero_with_error(self) -> None:
        """A path that does not exist must write to stderr and exit 1."""
        result = _run("scan", "/nonexistent/path/xyz")

        self.assertEqual(result.returncode, 1)
        self.assertTrue(
            result.stderr.strip(),
            msg="Expected error message in stderr for nonexistent directory",
        )

    # ------------------------------------------------------------------
    # T009 — User Story 2: extension filter
    # ------------------------------------------------------------------

    def test_ext_filter_includes_only_matching_files(self) -> None:
        """--ext .md must include only .md files; .py files must not appear."""
        with tempfile.TemporaryDirectory() as tmp:
            md_file = Path(tmp) / "readme.md"
            py_file = Path(tmp) / "script.py"
            md_file.write_text("# hello markdown", encoding="utf-8")
            py_file.write_text("print('hello python')", encoding="utf-8")

            result = _run("scan", tmp, "--ext", ".md")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        output = result.stdout

        self.assertIn("readme.md", output)
        self.assertNotIn("script.py", output)

    def test_ext_filter_no_match_reports_no_files_found(self) -> None:
        """--ext with an extension that matches nothing must report 'no files found', exit 0."""
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "readme.md").write_text("hello", encoding="utf-8")

            result = _run("scan", tmp, "--ext", ".xyz")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("no files found", result.stdout.lower())

    # ------------------------------------------------------------------
    # T010 — User Story 3: binary file handling
    # ------------------------------------------------------------------

    def test_binary_file_skipped_with_warning_text_file_shown(self) -> None:
        """Binary files must be skipped (not in stdout table); a warning
        mentioning 'binary' must appear in stderr; text files still appear;
        exit 0."""
        with tempfile.TemporaryDirectory() as tmp:
            bin_file = Path(tmp) / "image.bin"
            txt_file = Path(tmp) / "notes.txt"
            bin_file.write_bytes(b"\x00binary\x00\xff\xfe")
            txt_file.write_text("some readable text here", encoding="utf-8")

            result = _run("scan", tmp)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        stdout = result.stdout
        stderr = result.stderr.lower()

        # Binary file must NOT appear in the output table
        self.assertNotIn("image.bin", stdout)

        # A warning about the binary file must appear in stderr
        self.assertIn("warning", stderr)
        self.assertIn("binary", stderr)

        # Text file must still appear normally
        self.assertIn("notes.txt", stdout)

    # ------------------------------------------------------------------
    # Additional coverage gaps
    # ------------------------------------------------------------------

    def test_single_file_shows_one_row_and_total(self) -> None:
        """Scan a directory with only one text file; output must have header,
        one data row with the file, a total row, and exit 0."""
        with tempfile.TemporaryDirectory() as tmp:
            single_file = Path(tmp) / "single.txt"
            single_file.write_text("hello world test", encoding="utf-8")

            result = _run("scan", tmp)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        output = result.stdout
        output_lower = output.lower()

        # Header row
        self.assertIn("file", output_lower)
        self.assertIn("token", output_lower)
        self.assertIn("word", output_lower)

        # Single file appears
        self.assertIn("single.txt", output)

        # Total row present
        self.assertIn("total", output_lower)

    def test_ext_filter_multiple_extensions_shows_both(self) -> None:
        """--ext with multiple extensions (.md .txt) must include files matching
        either extension; .py files must not appear; exit 0."""
        with tempfile.TemporaryDirectory() as tmp:
            md_file = Path(tmp) / "a.md"
            txt_file = Path(tmp) / "b.txt"
            py_file = Path(tmp) / "c.py"
            md_file.write_text("# markdown file", encoding="utf-8")
            txt_file.write_text("text file content", encoding="utf-8")
            py_file.write_text("print('python')", encoding="utf-8")

            result = _run("scan", tmp, "--ext", ".md", ".txt")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        output = result.stdout

        # Both .md and .txt files must appear
        self.assertIn("a.md", output)
        self.assertIn("b.txt", output)

        # .py file must not appear
        self.assertNotIn("c.py", output)

    def test_all_binary_files_reports_no_files_found(self) -> None:
        """Scan a directory containing only binary files; output must report
        'no files found', a warning in stderr, and exit 0."""
        with tempfile.TemporaryDirectory() as tmp:
            bin_file1 = Path(tmp) / "file1.bin"
            bin_file2 = Path(tmp) / "file2.exe"
            bin_file1.write_bytes(b"\x00binary\x00\xff\xfe")
            bin_file2.write_bytes(b"\x4d\x5a\x90\x00")  # PE header

            result = _run("scan", tmp)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        output_lower = result.stdout.lower()
        stderr_lower = result.stderr.lower()

        # Must report no files found
        self.assertIn("no files found", output_lower)

        # Per-file warnings must appear in stderr
        self.assertIn("warning", stderr_lower)
        self.assertIn("file1.bin", result.stderr)
        self.assertIn("file2.exe", result.stderr)


if __name__ == "__main__":
    unittest.main()
