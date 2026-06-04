"""
dev.py — CLI utilities for Claude_Code_MVP development tasks.

Usage:
    python scripts/dev.py --help
    python scripts/dev.py token-count --help
    python scripts/dev.py compare --help
    python scripts/dev.py word-count --help
"""

import argparse
import sys
from pathlib import Path

import tiktoken


_enc = tiktoken.get_encoding("cl100k_base")

_SKIP_DIRS = frozenset(
    {".git", "node_modules", "__pycache__", ".venv", "dist", "build"}
)


def count_tokens(path: str) -> int:
    """Read *path* and return its token count using cl100k_base encoding."""
    text = Path(path).read_text(encoding="utf-8")
    return len(_enc.encode(text))


def _cmd_token_count(args: argparse.Namespace) -> None:
    missing = [f for f in args.files if not Path(f).exists()]
    if missing:
        for f in missing:
            print(f"error: file not found: {Path(f).name}", file=sys.stderr)
        raise SystemExit(1)

    counts = [(Path(f).name, count_tokens(f)) for f in args.files]
    for name, n in counts:
        print(f"{name}\t{n}")

    if len(counts) > 1:
        print("-" * 40)
        print(f"total\t{sum(n for _, n in counts)}")


def count_words(path: str) -> int:
    """Read *path* and return its word count using str.split()."""
    text = Path(path).read_text(encoding="utf-8")
    return len(text.split())


def _cmd_word_count(args: argparse.Namespace) -> None:
    missing = [f for f in args.files if not Path(f).exists()]
    if missing:
        for f in missing:
            print(f"error: file not found: {Path(f).name}", file=sys.stderr)
        raise SystemExit(1)

    counts = [(Path(f).name, count_words(f)) for f in args.files]
    for name, n in counts:
        print(f"{name}\t{n}")

    if len(counts) > 1:
        print("-" * 40)
        print(f"total\t{sum(n for _, n in counts)}")


def _is_binary(path: Path) -> bool:
    """Return True if *path* appears to be a binary file (contains a null byte)."""
    with path.open("rb") as fh:
        chunk = fh.read(1024)
    return b"\x00" in chunk


def _scan_files(
    directory: Path,
    exts: set[str],
    skip_dirs: frozenset[str],
) -> list[Path]:
    """Recursively collect text-candidate files under *directory*."""
    results: list[Path] = []
    for p in directory.rglob("*"):
        # Skip if any relative path component is in skip_dirs
        rel = p.relative_to(directory)
        if any(part in skip_dirs for part in rel.parts):
            continue
        if not p.is_file():
            continue
        if exts and p.suffix not in exts:
            continue
        results.append(p)
    return results


def _format_scan_table(rows: list[tuple[str, int, int]]) -> str:
    """Format scan results as a fixed-width table string."""
    if not rows:
        return "(no files)"
    file_col_width = max(4, max(len(r[0]) for r in rows)) + 2
    sep = "─" * (file_col_width + 8 + 8 + 2 * 2)

    header = f"{'file':<{file_col_width}}" f"  {'tokens':>8}" f"  {'words':>8}"
    lines = [header]
    for rel_path, tokens, words in rows:
        lines.append(f"{rel_path:<{file_col_width}}" f"  {tokens:>8}" f"  {words:>8}")
    lines.append(sep)

    total_tokens = sum(r[1] for r in rows)
    total_words = sum(r[2] for r in rows)
    n = len(rows)
    total_label = f"total ({n} files)"
    lines.append(
        f"{total_label:<{file_col_width}}" f"  {total_tokens:>8}" f"  {total_words:>8}"
    )
    return "\n".join(lines)


def _cmd_scan(args: argparse.Namespace) -> None:
    directory = Path(args.dir)
    if not directory.exists():
        print(f"error: directory not found: {directory}", file=sys.stderr)
        raise SystemExit(1)

    exts: set[str] = set(args.ext) if args.ext else set()
    candidates = _scan_files(directory, exts, _SKIP_DIRS)

    rows: list[tuple[str, int, int]] = []
    for p in candidates:
        rel_path = str(p.relative_to(directory))
        try:
            binary = _is_binary(p)
        except OSError as e:
            print(f"warning: skipped {rel_path} (unreadable: {e})", file=sys.stderr)
            continue
        if binary:
            print(f"warning: skipped {rel_path} (binary)", file=sys.stderr)
            continue
        try:
            tokens = count_tokens(str(p))
            words = count_words(str(p))
        except OSError as e:
            print(f"warning: skipped {rel_path} (unreadable: {e})", file=sys.stderr)
            continue
        rows.append((rel_path, tokens, words))

    if not rows:
        print("no files found")
        return

    rows.sort(key=lambda r: r[1], reverse=True)
    print(_format_scan_table(rows))


def _cmd_compare(args: argparse.Namespace) -> None:
    missing = [f for f in (args.baseline, args.target) if not Path(f).exists()]
    if missing:
        for f in missing:
            print(f"error: file not found: {Path(f).name}", file=sys.stderr)
        raise SystemExit(1)

    baseline_n = count_tokens(args.baseline)
    target_n = count_tokens(args.target)
    diff = target_n - baseline_n

    if baseline_n == 0:
        pct_str = "+0.0%" if diff == 0 else "N/A (baseline is 0 tokens)"
    else:
        pct = diff / baseline_n * 100
        sign = "+" if pct >= 0 else ""
        pct_str = f"{sign}{pct:.1f}%"

    sign = "+" if diff >= 0 else ""
    print(f"{Path(args.baseline).name}\t{baseline_n}")
    print(f"{Path(args.target).name}\t{target_n}")
    print("-" * 40)
    print(f"diff\t{sign}{diff} tokens ({pct_str})")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dev.py",
        description="Development utilities for Claude_Code_MVP.",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="<command>")

    # --- token-count ---
    token_count_parser = subparsers.add_parser(
        "token-count",
        help="Count tokens in one or more files.",
        description=(
            "Count the number of tokens in a file using the cl100k_base "
            "tiktoken encoding."
        ),
    )
    token_count_parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Path(s) to the file(s) to count tokens in.",
    )
    token_count_parser.set_defaults(func=_cmd_token_count)

    # --- compare ---
    compare_parser = subparsers.add_parser(
        "compare",
        help="Compare token usage across files or approaches.",
        description=(
            "Compare token counts between two files or measurement approaches."
        ),
    )
    compare_parser.add_argument(
        "baseline",
        metavar="BASELINE",
        help="Path to the baseline file.",
    )
    compare_parser.add_argument(
        "target",
        metavar="TARGET",
        help="Path to the target file to compare against the baseline.",
    )
    compare_parser.set_defaults(func=_cmd_compare)

    # --- word-count ---
    word_count_parser = subparsers.add_parser(
        "word-count",
        help="Count words in one or more files.",
        description=(
            "Count the number of words in a file. "
            "A word is any sequence of non-whitespace characters (str.split())."
        ),
    )
    word_count_parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Path(s) to the file(s) to count words in.",
    )
    word_count_parser.set_defaults(func=_cmd_word_count)

    # --- scan ---
    scan_parser = subparsers.add_parser(
        "scan",
        help="Scan a directory for text files and report token and word counts.",
        description=(
            "Recursively scan a directory, reporting token and word counts "
            "for each text file, sorted by token count descending. "
            "Skips binary files and common noise directories (.git, node_modules, etc.)."
        ),
    )
    scan_parser.add_argument("dir", metavar="DIR", help="Directory to scan.")
    scan_parser.add_argument(
        "--ext",
        nargs="+",
        metavar="EXT",
        default=None,
        help="Only include files with these extensions (e.g. --ext .md .txt). Case-sensitive, include the dot.",
    )
    scan_parser.set_defaults(func=_cmd_scan)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    try:
        args.func(args)
    except NotImplementedError as exc:
        parser.error(f"Not yet implemented: {exc}")


if __name__ == "__main__":
    main()
