#!/usr/bin/env python3
"""
Helper script to fetch post URLs from Substack archive page.
Use this if the sitemap is blocked.
"""

import re
import sys
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


def fetch_archive_urls(base_url: str, year: int = None, output_file: str = None):
    """Fetch post URLs from the archive page."""

    archive_url = f"{base_url}/archive"

    print(f"Fetching archive from: {archive_url}")

    # Use realistic headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none'
    }

    try:
        response = requests.get(archive_url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all post links - Substack usually uses specific patterns
        post_links = []

        # Look for links with /p/ pattern (typical for Substack posts)
        for link in soup.find_all('a', href=True):
            href = link['href']

            # Make absolute URL
            if href.startswith('/'):
                href = urljoin(base_url, href)

            # Filter for post URLs
            if '/p/' in href and base_url in href:
                # Extract year if possible
                if year:
                    # Check if year is in URL or link text
                    link_text = link.get_text()
                    if str(year) in href or str(year) in link_text:
                        post_links.append(href)
                else:
                    post_links.append(href)

        # Remove duplicates while preserving order
        seen = set()
        unique_links = []
        for link in post_links:
            if link not in seen:
                seen.add(link)
                unique_links.append(link)

        print(f"Found {len(unique_links)} post URLs")

        if output_file:
            with open(output_file, 'w') as f:
                f.write(f"# Post URLs from {base_url}\n")
                if year:
                    f.write(f"# Filtered for year: {year}\n")
                f.write(f"# Total: {len(unique_links)} URLs\n\n")

                for url in unique_links:
                    f.write(f"{url}\n")

            print(f"Saved to: {output_file}")
        else:
            print("\nURLs:")
            for url in unique_links:
                print(url)

        return unique_links

    except requests.exceptions.RequestException as e:
        print(f"Error fetching archive: {e}")
        print("\nThe archive page may be blocked by anti-bot protection.")
        print("You can manually copy URLs from your browser:")
        print(f"1. Visit {archive_url} in your browser")
        print(f"2. Copy post URLs (they should look like {base_url}/p/post-title)")
        print(f"3. Save them to a text file (one URL per line)")
        print(f"4. Run the link checker with: checker.run(url_file='your_file.txt', limit=10)")
        return []


if __name__ == '__main__':
    base_url = 'https://yoursubstack.substack.com'
    year = 2020
    output_file = 'post_urls_2020.txt'

    if len(sys.argv) > 1:
        year = int(sys.argv[1])
        output_file = f'post_urls_{year}.txt'

    fetch_archive_urls(base_url, year=year, output_file=output_file)

