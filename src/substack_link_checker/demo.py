#!/usr/bin/env python3
"""
Demo script showing how to use SubstackLinkChecker programmatically.

Tests the link checker against various URLs to demonstrate error detection.
"""

import asyncio

import aiohttp

from .checker import SubstackLinkChecker


async def demo_check_links():
    """Demonstrate link checking with various test URLs."""

    # Test URLs showcasing different error types
    test_urls = [
        ("https://www.example.com", "Working link"),
        ("https://httpstat.us/404", "HTTP 404 error"),
        ("https://this-domain-does-not-exist-12345.com", "DNS failure"),
        ("https://httpstat.us/200", "Working link"),
        ("https://httpstat.us/500", "HTTP 500 error"),
        ("https://expired.badssl.com", "SSL certificate error"),
    ]

    # Initialize checker (base_url doesn't matter for direct link tests)
    checker = SubstackLinkChecker(base_url="https://example.substack.com", timeout=10, verbose=True)

    print("=" * 60)
    print("SUBSTACK LINK CHECKER - DEMO")
    print("=" * 60)
    print()

    # Create aiohttp session for checking
    connector = aiohttp.TCPConnector(limit=5, ssl=True)
    async with aiohttp.ClientSession(
        connector=connector, headers=checker.DEFAULT_HEADERS
    ) as session:
        for url, description in test_urls:
            print(f"Testing: {description}")
            print(f"  URL: {url}")

            result = await checker.check_link_with_retry(session, url)

            if result.is_broken:
                print(f"  ✗ BROKEN - {result.error_type}")
            else:
                print(f"  ✓ OK - {result.error_type}")
            print()

    print("=" * 60)
    print("Demo complete!")
    print()
    print("To check your own Substack, run:")
    print(
        "  python substack_link_checker.py --base-url https://YOUR-SUBSTACK.substack.com --year 2024"
    )


def main():
    """Run the demo."""
    import argparse

    argparse.ArgumentParser(
        description=(
            "Self-contained demo: runs the link checker against a handful "
            "of known-good and known-bad URLs. Takes no arguments. Useful "
            "for verifying your install before pointing at a real Substack."
        ),
    ).parse_args()
    asyncio.run(demo_check_links())


if __name__ == "__main__":
    main()
