#!/usr/bin/env python3
"""
Fetch post URLs from a Substack archive page.

Use this as a fallback when the sitemap doesn't work or you need to filter
by specific criteria. The main `check` subcommand's --year option is
usually easier.
"""

import argparse

import requests
from bs4 import BeautifulSoup


def fetch_archive_urls(base_url, year=None):
    """
    Fetch post URLs from a Substack archive page.

    Args:
        base_url: Base Substack URL (e.g., https://example.substack.com)
        year: Optional year to filter posts

    Returns:
        List of post URLs
    """
    archive_url = f"{base_url.rstrip('/')}/archive"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
    }

    print(f"Fetching archive from {archive_url}...")

    try:
        response = requests.get(archive_url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching archive: {e}")
        print(f"\nTry visiting {archive_url} in your browser and manually copying URLs.")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    # Find all links that look like posts (/p/ pattern)
    post_urls = set()
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "/p/" in href:
            # Make absolute URL if relative
            if href.startswith("/"):
                href = base_url.rstrip("/") + href
            # Filter by year if specified
            if year:
                year_str = str(year)
                link_text = link.get_text()
                if year_str in href or year_str in link_text:
                    post_urls.add(href)
            else:
                post_urls.add(href)

    # Sort by URL (roughly chronological for Substack)
    sorted_urls = sorted(post_urls)

    print(f"Found {len(sorted_urls)} posts" + (f" from {year}" if year else ""))

    return sorted_urls


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Scrape post URLs from a Substack's /archive page. Fallback "
            "when the sitemap is missing or incomplete; prefer the "
            "`check --year` flow when it works."
        ),
    )
    parser.add_argument(
        "base_url",
        help="Base URL of the Substack (e.g. https://example.substack.com)",
    )
    parser.add_argument(
        "year",
        nargs="?",
        type=int,
        default=None,
        help="Optional year filter (matches against URL slug and link text).",
    )
    args = parser.parse_args()

    base_url = args.base_url
    year = args.year

    urls = fetch_archive_urls(base_url, year)

    if urls:
        filename = f"archive_urls{'_' + str(year) if year else ''}.txt"
        with open(filename, "w") as f:
            for url in urls:
                f.write(url + "\n")
        print(f"\nSaved to: {filename}")
        print("\nTo check these posts, run:")
        print(f"  substack-link-checker check --base-url {base_url} --url-file {filename}")


if __name__ == "__main__":
    main()
