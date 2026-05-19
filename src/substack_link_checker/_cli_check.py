"""CLI for the `check` subcommand (the main link-checking workflow)."""

import argparse
import os
import sys
from typing import List, Optional

from .checker import SubstackLinkChecker


def load_domains_from_file(file_path: str) -> List[str]:
    """Load domains from a text file (one domain per line)."""
    domains: List[str] = []
    try:
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    domains.append(line)
        return domains
    except FileNotFoundError:
        print(f"Warning: Domain file not found: {file_path}")
        return []
    except OSError as e:
        print(f"Warning: Error reading domain file: {e}")
        return []


def build_parser(prog: Optional[str] = None) -> argparse.ArgumentParser:
    """Build the argparse parser for the check subcommand.

    Used both as a top-level parser (legacy `python substack_link_checker.py`
    shim) and as the parser for `substack-link-checker check ...`.
    """
    parser = argparse.ArgumentParser(
        prog=prog,
        description="Check for broken links in Substack newsletter posts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check posts from a URL file
  %(prog)s --base-url https://example.substack.com --url-file posts.txt

  # Check with higher concurrency and custom output
  %(prog)s --base-url https://example.substack.com --url-file posts.txt \\
           --concurrency 20 --output my_report.csv

  # Limit to first 5 posts with verbose output
  %(prog)s --base-url https://example.substack.com --url-file posts.txt \\
           --limit 5 --verbose

  # Track checked posts and only scan new ones on subsequent runs
  %(prog)s --base-url https://example.substack.com --url-file posts.txt \\
           --history-file checked_posts.json

  # Only check posts not previously scanned
  %(prog)s --base-url https://example.substack.com --url-file posts.txt \\
           --history-file checked_posts.json --only-new

  # Skip bot-blocking domains and auto-flag known broken domains
  %(prog)s --base-url https://example.substack.com --url-file posts.txt \\
           --skip-domains wikipedia.org ko-fi.com \\
           --broken-domains local.example.com defunct.site.com
        """,
    )

    parser.add_argument(
        "--base-url",
        "-b",
        required=True,
        help="Base URL of the Substack (e.g., https://example.substack.com)",
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--year", "-y", type=int, help="Year to check posts from (uses sitemap)"
    )
    input_group.add_argument(
        "--url-file", "-f", help="Path to file containing post URLs (one per line)"
    )

    parser.add_argument("--limit", "-l", type=int, help="Maximum number of posts to check")
    parser.add_argument(
        "--output",
        "-o",
        default="broken_links_report.csv",
        help="Output CSV filename (default: broken_links_report.csv)",
    )
    parser.add_argument(
        "--concurrency",
        "-c",
        type=int,
        default=10,
        help="Maximum concurrent requests (default: 10)",
    )
    parser.add_argument(
        "--timeout", "-t", type=int, default=10, help="Request timeout in seconds (default: 10)"
    )
    parser.add_argument(
        "--max-retries",
        "-r",
        type=int,
        default=3,
        help="Maximum retry attempts for transient failures (default: 3)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")

    parser.add_argument(
        "--history-file",
        "-H",
        help="Path to JSON file for tracking checked posts (enables incremental scanning)",
    )
    parser.add_argument(
        "--only-new",
        action="store_true",
        help="Only check posts not in history (requires --history-file)",
    )
    parser.add_argument(
        "--skip-domains",
        "-S",
        nargs="+",
        default=["wikipedia.org"],
        help=(
            "Domains to skip checking and assume OK (default: wikipedia.org). "
            "Use --skip-domains none to check all."
        ),
    )
    parser.add_argument(
        "--skip-domains-file", help="File containing domains to skip (one per line)"
    )
    parser.add_argument(
        "--broken-domains",
        "-B",
        nargs="+",
        default=[],
        help="Domains to auto-flag as broken without checking (e.g., local.example.com)",
    )
    parser.add_argument(
        "--broken-domains-file",
        help="File containing domains to auto-flag as broken (one per line)",
    )
    parser.add_argument(
        "--cookie",
        "-C",
        help=(
            "Substack session cookie (substack.sid) for authenticated access "
            "to paywalled content. WARNING: passing this on the command line "
            "exposes it in shell history and process listings; prefer the "
            "SUBSTACK_COOKIE environment variable instead."
        ),
    )

    return parser


def run(args: argparse.Namespace) -> None:
    """Execute the check command from already-parsed args."""
    if args.only_new and not args.history_file:
        print("Error: --only-new requires --history-file to be specified")
        sys.exit(1)

    skip_domains = [] if args.skip_domains == ["none"] else list(args.skip_domains)
    if args.skip_domains_file:
        skip_domains.extend(load_domains_from_file(args.skip_domains_file))
    skip_domains = skip_domains if skip_domains else None

    broken_domains = list(args.broken_domains) if args.broken_domains else []
    if args.broken_domains_file:
        broken_domains.extend(load_domains_from_file(args.broken_domains_file))
    broken_domains = broken_domains if broken_domains else None

    # Prefer SUBSTACK_COOKIE env var; --cookie takes precedence if both set
    # so users can override an exported env var ad-hoc.
    cookie = args.cookie or os.environ.get("SUBSTACK_COOKIE")

    checker = SubstackLinkChecker(
        base_url=args.base_url,
        timeout=args.timeout,
        concurrency=args.concurrency,
        max_retries=args.max_retries,
        verbose=args.verbose,
        skip_domains=skip_domains,
        broken_domains=broken_domains,
        cookie=cookie,
    )

    checker.run(
        year=args.year,
        limit=args.limit,
        output_file=args.output,
        url_file=args.url_file,
        history_file=args.history_file,
        only_new=args.only_new,
    )


def main() -> None:
    """Entry point for `python substack_link_checker.py ...` (legacy shim)."""
    parser = build_parser()
    args = parser.parse_args()
    run(args)
