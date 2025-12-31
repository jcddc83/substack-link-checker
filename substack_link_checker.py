#!/usr/bin/env python3
"""
Substack Broken Link Checker
Checks links from Substack posts and generates a CSV report of broken links.

Features:
- Async concurrent link checking for 10-20x speedup
- Global link cache to avoid redundant checks
- Retry logic with exponential backoff
- Full CLI interface
"""

import argparse
import asyncio
import csv
import re
import sys
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET

import aiohttp
import requests
from bs4 import BeautifulSoup


@dataclass
class LinkCheckResult:
    """Result of checking a single link."""
    is_broken: bool
    error_type: str
    from_cache: bool = False


@dataclass
class BrokenLinkRecord:
    """Record of a broken link for reporting."""
    post_title: str
    post_url: str
    broken_link: str
    error_type: str


class SubstackLinkChecker:
    """
    Async link checker for Substack newsletters.

    Features:
    - Concurrent link checking with configurable parallelism
    - Global link cache to avoid re-checking the same URLs
    - Retry logic with exponential backoff for transient failures
    - Multiple input modes (sitemap, file, direct URLs)
    """

    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    # Soft 404 detection patterns
    SOFT_404_PATTERNS = [
        '404 error', 'page not found', 'not found', '404',
        'page doesn\'t exist', 'page does not exist',
        'no longer available', 'has been removed',
        'couldn\'t find', 'could not find'
    ]

    def __init__(
        self,
        base_url: str,
        timeout: int = 10,
        concurrency: int = 10,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        verbose: bool = False
    ):
        """
        Initialize the link checker.

        Args:
            base_url: Base URL of the Substack (e.g., https://example.substack.com)
            timeout: Request timeout in seconds
            concurrency: Maximum number of concurrent requests
            max_retries: Maximum retry attempts for transient failures
            retry_delay: Base delay between retries (doubles each attempt)
            verbose: Enable verbose output
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.concurrency = concurrency
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.verbose = verbose

        # Synchronous session for sitemap/post fetching
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)

        # Global link cache: url -> LinkCheckResult
        self.link_cache: Dict[str, LinkCheckResult] = {}

        # Results storage
        self.results: List[BrokenLinkRecord] = []

        # Statistics
        self.stats = {
            'total_links_checked': 0,
            'cache_hits': 0,
            'broken_links': 0,
            'retries': 0
        }

    def _log(self, message: str, force: bool = False):
        """Print message if verbose mode is enabled or force is True."""
        if self.verbose or force:
            print(message)

    def fetch_sitemap(self) -> List[str]:
        """Fetch and parse the sitemap to get post URLs."""
        sitemap_url = f"{self.base_url}/sitemap.xml"
        self._log(f"Fetching sitemap from {sitemap_url}...", force=True)

        try:
            response = self.session.get(sitemap_url, timeout=self.timeout)
            response.raise_for_status()

            root = ET.fromstring(response.content)
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

            # Check if this is a sitemap index
            sitemaps = root.findall('.//ns:sitemap/ns:loc', namespace)
            if sitemaps:
                self._log(f"Found sitemap index with {len(sitemaps)} sitemaps", force=True)
                return [sitemap.text for sitemap in sitemaps]

            # Otherwise, get URLs from this sitemap
            urls = root.findall('.//ns:url/ns:loc', namespace)
            return [url.text for url in urls]

        except requests.exceptions.RequestException as e:
            print(f"Error fetching sitemap: {e}")
            return []
        except ET.ParseError as e:
            print(f"Error parsing sitemap XML: {e}")
            return []

    def filter_posts_by_year(self, urls: List[str], year: int) -> List[str]:
        """Filter URLs to only include posts from a specific year."""
        filtered = []
        year_str = str(year)
        for url in urls:
            if f"/{year_str}/" in url or f"-{year_str}-" in url:
                filtered.append(url)
        return filtered

    def get_post_urls_from_year_sitemap(self, year: int, limit: Optional[int] = None) -> List[str]:
        """Get post URLs from a specific year's sitemap."""
        all_urls = self.fetch_sitemap()

        # If we got a sitemap index, fetch the year-specific one
        year_sitemap = None
        for url in all_urls:
            if str(year) in url and 'sitemap' in url:
                year_sitemap = url
                break

        if year_sitemap:
            self._log(f"Fetching year-specific sitemap: {year_sitemap}", force=True)
            try:
                response = self.session.get(year_sitemap, timeout=self.timeout)
                response.raise_for_status()

                root = ET.fromstring(response.content)
                namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                urls = root.findall('.//ns:url/ns:loc', namespace)
                post_urls = [url.text for url in urls]

                if limit:
                    post_urls = post_urls[:limit]

                self._log(f"Found {len(post_urls)} posts from {year}", force=True)
                return post_urls
            except Exception as e:
                print(f"Error fetching year sitemap: {e}")

        # Fallback: filter from all URLs
        filtered = self.filter_posts_by_year(all_urls, year)
        if limit:
            filtered = filtered[:limit]
        return filtered

    def load_urls_from_file(self, file_path: str, limit: Optional[int] = None) -> List[str]:
        """Load post URLs from a text file (one URL per line)."""
        self._log(f"Loading URLs from {file_path}...", force=True)

        try:
            with open(file_path, 'r') as f:
                urls = [
                    line.strip() for line in f
                    if line.strip() and line.strip().startswith('http')
                ]

            if limit:
                urls = urls[:limit]

            self._log(f"Loaded {len(urls)} URLs from file", force=True)
            return urls
        except FileNotFoundError:
            print(f"Error: File not found: {file_path}")
            return []
        except IOError as e:
            print(f"Error loading URLs from file: {e}")
            return []

    def extract_links_from_post(self, post_url: str) -> Tuple[str, List[str]]:
        """Extract all links from a post and return the post title."""
        self._log(f"  Extracting links from {post_url}...")

        try:
            response = self.session.get(post_url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Get post title
            title_tag = soup.find('h1') or soup.find('title')
            title = title_tag.get_text(strip=True) if title_tag else "Unknown Title"

            # Extract all links from the post content
            content_area = soup.find('article') or soup.find('div', class_=re.compile('post|article|content'))

            if content_area:
                links = [a['href'] for a in content_area.find_all('a', href=True)]
            else:
                links = [a['href'] for a in soup.find_all('a', href=True)]

            # Filter and normalize links
            external_links = []
            for link in links:
                # Skip anchors, mailto, tel, etc.
                if link.startswith('#') or link.startswith('mailto:') or link.startswith('tel:'):
                    continue

                # Skip Substack internal links (comments, share, etc.)
                if 'substack.com' in link and any(x in link for x in ['/subscribe', '/comments', '/share']):
                    continue

                # Make relative URLs absolute
                if link.startswith('/') or not link.startswith('http'):
                    link = urljoin(post_url, link)

                external_links.append(link)

            # Remove duplicates while preserving order
            seen: Set[str] = set()
            unique_links = []
            for link in external_links:
                if link not in seen:
                    seen.add(link)
                    unique_links.append(link)

            self._log(f"    Found {len(unique_links)} unique links")
            return title, unique_links

        except requests.exceptions.RequestException as e:
            self._log(f"    Error extracting links: {e}")
            return "Error fetching post", []

    async def _check_link_once(
        self,
        session: aiohttp.ClientSession,
        link: str
    ) -> Tuple[bool, str, bool]:
        """
        Check a link once (no retries).

        Returns: (is_broken, error_type, should_retry)
        """
        try:
            # Special case: known problematic domains
            if 'local.theonion.com' in link:
                return True, "SSL Error (local.theonion.com)", False

            async with session.get(
                link,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                allow_redirects=True,
                ssl=True
            ) as response:
                # Check for HTTP errors
                if response.status == 404:
                    return True, "HTTP 404", False

                if response.status >= 500:
                    # Server errors are retryable
                    return True, f"HTTP {response.status}", True

                if response.status >= 400:
                    return True, f"HTTP {response.status}", False

                # Check for soft 404s in the page title
                try:
                    content = await response.text()
                    soup = BeautifulSoup(content, 'html.parser')
                    title = soup.find('title')
                    if title:
                        title_text = title.get_text().lower()
                        if any(phrase in title_text for phrase in self.SOFT_404_PATTERNS):
                            return True, "Soft 404 (page title indicates error)", False
                except Exception:
                    pass  # If we can't parse, assume it's OK

                return False, "OK", False

        except asyncio.TimeoutError:
            return True, "Timeout", True
        except aiohttp.ClientSSLError as e:
            return True, f"SSL Error: {str(e)[:80]}", False
        except aiohttp.ClientConnectorError as e:
            error_str = str(e)
            # DNS failures are not retryable
            if 'Name or service not known' in error_str or 'nodename nor servname' in error_str:
                return True, "DNS Failure", False
            # Other connection errors might be transient
            return True, f"Connection Error: {error_str[:80]}", True
        except aiohttp.ClientError as e:
            return True, f"Client Error: {str(e)[:80]}", True
        except Exception as e:
            return True, f"Unknown Error: {str(e)[:80]}", False

    async def check_link_with_retry(
        self,
        session: aiohttp.ClientSession,
        link: str
    ) -> LinkCheckResult:
        """
        Check a link with retry logic and exponential backoff.

        Returns: LinkCheckResult
        """
        # Check cache first
        if link in self.link_cache:
            self.stats['cache_hits'] += 1
            cached = self.link_cache[link]
            return LinkCheckResult(cached.is_broken, cached.error_type, from_cache=True)

        self.stats['total_links_checked'] += 1

        delay = self.retry_delay
        last_error = "Unknown"

        for attempt in range(self.max_retries + 1):
            is_broken, error_type, should_retry = await self._check_link_once(session, link)

            if not is_broken:
                result = LinkCheckResult(False, "OK")
                self.link_cache[link] = result
                return result

            last_error = error_type

            if not should_retry or attempt == self.max_retries:
                break

            # Exponential backoff
            self.stats['retries'] += 1
            self._log(f"    Retry {attempt + 1}/{self.max_retries} for {link[:60]}... (waiting {delay:.1f}s)")
            await asyncio.sleep(delay)
            delay *= 2  # Exponential backoff

        result = LinkCheckResult(True, last_error)
        self.link_cache[link] = result
        self.stats['broken_links'] += 1
        return result

    async def check_links_batch(
        self,
        links: List[str],
        post_title: str,
        post_url: str
    ) -> List[BrokenLinkRecord]:
        """
        Check a batch of links concurrently.

        Returns: List of broken link records
        """
        broken_records = []

        connector = aiohttp.TCPConnector(limit=self.concurrency, ssl=True)
        async with aiohttp.ClientSession(
            connector=connector,
            headers=self.DEFAULT_HEADERS
        ) as session:
            # Create semaphore to limit concurrency
            semaphore = asyncio.Semaphore(self.concurrency)

            async def check_with_semaphore(link: str) -> Tuple[str, LinkCheckResult]:
                async with semaphore:
                    result = await self.check_link_with_retry(session, link)
                    # Small delay between requests to be polite
                    await asyncio.sleep(0.1)
                    return link, result

            # Check all links concurrently
            tasks = [check_with_semaphore(link) for link in links]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for item in results:
                if isinstance(item, Exception):
                    self._log(f"    Unexpected error: {item}")
                    continue

                link, result = item
                if result.is_broken:
                    cache_note = " (cached)" if result.from_cache else ""
                    self._log(f"    ✗ BROKEN{cache_note}: {link[:70]}... ({result.error_type})")
                    broken_records.append(BrokenLinkRecord(
                        post_title=post_title,
                        post_url=post_url,
                        broken_link=link,
                        error_type=result.error_type
                    ))

        return broken_records

    async def check_post_links_async(self, post_url: str):
        """Check all links in a post asynchronously."""
        title, links = self.extract_links_from_post(post_url)

        if not links:
            self._log(f"  No links found in this post\n")
            return

        # Count how many are cached
        cached_count = sum(1 for link in links if link in self.link_cache)
        new_count = len(links) - cached_count

        self._log(f"  Checking {len(links)} links ({new_count} new, {cached_count} cached)...")

        broken_records = await self.check_links_batch(links, title, post_url)
        self.results.extend(broken_records)

        self._log(f"  Found {len(broken_records)} broken links in this post\n")

    def generate_report(self, output_file: str = 'broken_links_report.csv'):
        """Generate a CSV report of broken links."""
        print(f"\n{'=' * 50}")
        print("SUMMARY")
        print(f"{'=' * 50}")
        print(f"Total links checked: {self.stats['total_links_checked']}")
        print(f"Cache hits: {self.stats['cache_hits']}")
        print(f"Retries performed: {self.stats['retries']}")
        print(f"Broken links found: {len(self.results)}")

        if not self.results:
            print("\nNo broken links found!")
            return

        print(f"\nGenerating report: {output_file}")

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=['post_title', 'post_url', 'broken_link', 'error_type']
            )
            writer.writeheader()
            for record in self.results:
                writer.writerow({
                    'post_title': record.post_title,
                    'post_url': record.post_url,
                    'broken_link': record.broken_link,
                    'error_type': record.error_type
                })

        print(f"Report generated with {len(self.results)} broken links")

    async def run_async(
        self,
        year: Optional[int] = None,
        limit: Optional[int] = None,
        output_file: str = 'broken_links_report.csv',
        url_file: Optional[str] = None
    ):
        """
        Main async entry point to run the link checker.

        Args:
            year: Year to check (if using sitemap)
            limit: Maximum number of posts to check
            output_file: Output CSV filename
            url_file: Path to file containing URLs (one per line)
        """
        print("Substack Broken Link Checker")
        print(f"{'=' * 50}")
        print(f"Base URL: {self.base_url}")
        print(f"Concurrency: {self.concurrency}")
        print(f"Max retries: {self.max_retries}")

        # Get post URLs
        if url_file:
            print(f"Mode: File input")
            print(f"URL file: {url_file}")
            post_urls = self.load_urls_from_file(url_file, limit)
        elif year:
            print(f"Mode: Sitemap")
            print(f"Year: {year}")
            post_urls = self.get_post_urls_from_year_sitemap(year, limit)
        else:
            print("Error: Must provide either 'year' or 'url_file'")
            return

        if limit:
            print(f"Post limit: {limit}")

        print(f"{'=' * 50}\n")

        if not post_urls:
            print("No posts found!")
            return

        start_time = time.time()

        # Check each post
        for i, post_url in enumerate(post_urls, 1):
            print(f"[{i}/{len(post_urls)}] Processing: {post_url}")
            await self.check_post_links_async(post_url)

        elapsed = time.time() - start_time
        print(f"\nCompleted in {elapsed:.1f} seconds")

        # Generate report
        self.generate_report(output_file)

    def run(
        self,
        year: Optional[int] = None,
        limit: Optional[int] = None,
        output_file: str = 'broken_links_report.csv',
        url_file: Optional[str] = None
    ):
        """
        Synchronous wrapper for run_async.

        Maintains backward compatibility with the original API.
        """
        asyncio.run(self.run_async(year, limit, output_file, url_file))


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Check for broken links in Substack newsletter posts.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check posts from 2020 using sitemap
  %(prog)s --base-url https://example.substack.com --year 2020

  # Check posts from a URL file
  %(prog)s --base-url https://example.substack.com --url-file posts.txt

  # Check with higher concurrency and custom output
  %(prog)s --base-url https://example.substack.com --url-file posts.txt \\
           --concurrency 20 --output my_report.csv

  # Limit to first 5 posts with verbose output
  %(prog)s --base-url https://example.substack.com --year 2020 \\
           --limit 5 --verbose
        """
    )

    # Required arguments
    parser.add_argument(
        '--base-url', '-b',
        required=True,
        help='Base URL of the Substack (e.g., https://example.substack.com)'
    )

    # Input source (one required)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--year', '-y',
        type=int,
        help='Year to check posts from (uses sitemap)'
    )
    input_group.add_argument(
        '--url-file', '-f',
        help='Path to file containing post URLs (one per line)'
    )

    # Optional arguments
    parser.add_argument(
        '--limit', '-l',
        type=int,
        help='Maximum number of posts to check'
    )
    parser.add_argument(
        '--output', '-o',
        default='broken_links_report.csv',
        help='Output CSV filename (default: broken_links_report.csv)'
    )
    parser.add_argument(
        '--concurrency', '-c',
        type=int,
        default=10,
        help='Maximum concurrent requests (default: 10)'
    )
    parser.add_argument(
        '--timeout', '-t',
        type=int,
        default=10,
        help='Request timeout in seconds (default: 10)'
    )
    parser.add_argument(
        '--max-retries', '-r',
        type=int,
        default=3,
        help='Maximum retry attempts for transient failures (default: 3)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )

    return parser.parse_args()


def main():
    """Main entry point with CLI support."""
    args = parse_args()

    checker = SubstackLinkChecker(
        base_url=args.base_url,
        timeout=args.timeout,
        concurrency=args.concurrency,
        max_retries=args.max_retries,
        verbose=args.verbose
    )

    checker.run(
        year=args.year,
        limit=args.limit,
        output_file=args.output,
        url_file=args.url_file
    )


if __name__ == '__main__':
    main()
