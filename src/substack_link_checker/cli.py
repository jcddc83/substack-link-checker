"""Top-level CLI dispatcher with subcommands.

Usage:
    substack-link-checker check ...        # run the link checker
    substack-link-checker compare ...      # diff sitemap vs history
    substack-link-checker import ...       # import previous results from Excel/CSV
    substack-link-checker fetch-archive ...# scrape archive page for post URLs
    substack-link-checker demo             # run a self-contained demo

Each subcommand delegates to a per-module `main()` function.
"""

import argparse
import sys
from typing import List, Optional

from . import __version__, _cli_check, compare, demo, fetch_archive, import_history

SUBCOMMANDS = {
    "check": (
        "Scan a Substack archive for broken links (the main command).",
        _cli_check.main,
    ),
    "compare": (
        "Compare your Substack sitemap against a checked-posts history file.",
        compare.main,
    ),
    "import": (
        "Import previously checked posts from Excel/CSV into the history file.",
        import_history.main,
    ),
    "fetch-archive": (
        "Fallback: scrape post URLs from the /archive page (use --year on `check` first).",
        fetch_archive.main,
    ),
    "demo": (
        "Run a self-contained demo against a handful of known-good and known-bad URLs.",
        demo.main,
    ),
}


def main(argv: Optional[List[str]] = None) -> None:
    """Top-level entry point: dispatch to the chosen subcommand."""
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="substack-link-checker",
        description="Substack Broken Link Checker — async link checker for Substack newsletters.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=("Run `substack-link-checker <subcommand> --help` for subcommand-specific options."),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="subcommand", metavar="<subcommand>")
    sub.required = True
    for name, (help_text, _) in SUBCOMMANDS.items():
        sub.add_parser(name, help=help_text, add_help=False)

    # We don't let argparse parse the subcommand's args — we just route to it
    # so that each module's own parser handles --help correctly with its own
    # epilog, examples, etc.
    if not argv or argv[0] in ("-h", "--help"):
        parser.print_help()
        return
    if argv[0] == "--version":
        parser.parse_args(argv)  # raises SystemExit(0) after printing version
        return

    name = argv[0]
    if name not in SUBCOMMANDS:
        parser.error(f"unknown subcommand: {name!r} (choose from {', '.join(SUBCOMMANDS)})")

    # Hand off remaining args to the subcommand's own argparse parser by
    # patching sys.argv. Each subcommand main() reads from sys.argv.
    original_argv = sys.argv
    try:
        sys.argv = [f"substack-link-checker {name}", *argv[1:]]
        SUBCOMMANDS[name][1]()
    finally:
        sys.argv = original_argv
