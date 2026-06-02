"""
dev.py — CLI utilities for Claude_Code_MVP development tasks.

Usage:
    python scripts/dev.py --help
    python scripts/dev.py token-count --help
    python scripts/dev.py compare --help
"""
import argparse
from pathlib import Path

import tiktoken


_enc = tiktoken.get_encoding("cl100k_base")


def count_tokens(path: str) -> int:
    """Read *path* and return its token count using cl100k_base encoding."""
    text = Path(path).read_text(encoding="utf-8")
    return len(_enc.encode(text))


def _cmd_token_count(args: argparse.Namespace) -> None:
    # Placeholder — to be implemented
    raise NotImplementedError("token-count subcommand is not implemented yet")


def _cmd_compare(args: argparse.Namespace) -> None:
    # Placeholder — to be implemented
    raise NotImplementedError("compare subcommand is not implemented yet")


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
