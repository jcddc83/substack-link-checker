#!/usr/bin/env python3
"""Compare sitemap posts against checked history."""

import argparse
import json
import xml.etree.ElementTree as ET

import requests


def get_sitemap_posts(base_url):
    """Get all post URLs from the sitemap."""
    sitemap_url = f"{base_url}/sitemap.xml"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(sitemap_url, headers=headers, timeout=10)
    response.raise_for_status()

    root = ET.fromstring(response.content)
    namespace = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    urls = root.findall(".//ns:url/ns:loc", namespace)
    # Filter to only /p/ posts (not /about, /archive, etc.)
    posts = [url.text for url in urls if "/p/" in url.text]
    return posts


def load_history(history_file):
    """Load checked posts from history file."""
    try:
        with open(history_file) as f:
            data = json.load(f)
            return set(data.get("checked_posts", {}).keys())
    except FileNotFoundError:
        return set()


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Compare your Substack sitemap against a checked-posts history "
            "file and list any posts not yet checked. Also writes the "
            "unchecked URLs to unchecked_posts.txt for use with "
            "`substack-link-checker check --url-file`."
        ),
    )
    parser.add_argument(
        "base_url",
        help="Base URL of the Substack (e.g. https://example.substack.com)",
    )
    parser.add_argument(
        "history_file",
        nargs="?",
        default="checked_posts.json",
        help="Path to the history file (default: checked_posts.json)",
    )
    args = parser.parse_args()

    base_url = args.base_url
    history_file = args.history_file

    print(f"Fetching posts from {base_url}/sitemap.xml...")
    sitemap_posts = get_sitemap_posts(base_url)
    checked_posts = load_history(history_file)

    sitemap_set = set(sitemap_posts)
    unchecked = sitemap_set - checked_posts
    checked = sitemap_set & checked_posts

    print(f"\n{'=' * 50}")
    print("COMPARISON RESULTS")
    print(f"{'=' * 50}")
    print(f"Total posts in sitemap: {len(sitemap_posts)}")
    print(f"Already checked:        {len(checked)}")
    print(f"Not yet checked:        {len(unchecked)}")
    print(f"{'=' * 50}\n")

    if unchecked:
        print("UNCHECKED POSTS:")
        for url in sorted(unchecked):
            print(f"  {url}")

        # Optionally save unchecked to file
        with open("unchecked_posts.txt", "w") as f:
            for url in sorted(unchecked):
                f.write(url + "\n")
        print("\nSaved unchecked URLs to: unchecked_posts.txt")


if __name__ == "__main__":
    main()
