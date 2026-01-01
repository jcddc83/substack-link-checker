# Substack Broken Link Checker

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A fast, async Python tool to find broken links in your Substack newsletter archive.

## Why This Tool?

Checking broken links in your newsletter archive shouldn't cost $100+/month for tools like Semrush or Ahrefs. This free, open-source tool:

- **Works with Substack's bot protection** - Uses your session cookie to authenticate as a logged-in user
- **Handles large archives efficiently** - Async concurrent checking is 10-20x faster than sequential
- **Tracks what you've already checked** - Incremental scanning means you only check new posts

## Features

- **Fast**: Async concurrent checking (10-20x faster than sequential)
- **Smart caching**: Same link across multiple posts? Checked once
- **Retry logic**: Exponential backoff for transient failures
- **Incremental scanning**: Track checked posts, only scan new ones
- **Domain filtering**: Skip bot-blocking sites (Wikipedia), auto-flag known broken domains
- **Multiple error types**: HTTP 404, soft 404s, SSL errors, DNS failures, timeouts

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Check all posts from 2024
python substack_link_checker.py --base-url https://YOUR.substack.com --year 2024

# Check posts from a file
python substack_link_checker.py --base-url https://YOUR.substack.com --url-file posts.txt
```

## Installation

```bash
git clone https://github.com/jcddc83/substack-link-checker.git
cd substack-link-checker
pip install -r requirements.txt
```

**Requirements**: Python 3.8+

## Authentication (Optional)

If Substack blocks your requests or you need to check paywalled content, use your session cookie:

1. Log into your Substack in a browser
2. Open Developer Tools (F12) → Application → Cookies
3. Find the `substack.sid` cookie and copy its value
4. Use it with the `--cookie` flag:

```bash
python substack_link_checker.py --base-url https://YOUR.substack.com --year 2024 \
    --cookie "your-substack-sid-cookie-value"
```

**Note:** Your session cookie expires after a few weeks. If you start getting 403 errors, get a fresh cookie from your browser.

## Usage

### Basic Usage

```bash
# Check posts from a specific year (uses sitemap)
python substack_link_checker.py --base-url https://example.substack.com --year 2024

# Check posts from a URL file
python substack_link_checker.py --base-url https://example.substack.com --url-file posts.txt

# Verbose output with custom report name
python substack_link_checker.py --base-url https://example.substack.com --year 2024 \
    --verbose --output december_report.csv
```

### Incremental Scanning (Recommended)

Track which posts you've already checked to avoid re-scanning:

```bash
# First run: checks all posts, saves history
python substack_link_checker.py --base-url https://example.substack.com --year 2024 \
    --history-file checked_posts.json

# Subsequent runs: only check new posts
python substack_link_checker.py --base-url https://example.substack.com --year 2024 \
    --history-file checked_posts.json --only-new
```

### Domain Filtering

```bash
# Skip domains that block bots (assumed OK)
python substack_link_checker.py ... --skip-domains wikipedia.org

# Auto-flag domains as broken without checking
python substack_link_checker.py ... --broken-domains old.defunct-site.com
```

### Finding Unchecked Posts

```bash
# Compare your sitemap against history to find unchecked posts
python compare_posts.py https://example.substack.com checked_posts.json
# Outputs: unchecked_posts.txt

# Then check just those posts
python substack_link_checker.py --base-url https://example.substack.com \
    --url-file unchecked_posts.txt --history-file checked_posts.json
```

## Example Output

```
$ python substack_link_checker.py --base-url https://example.substack.com --year 2024

Substack Broken Link Checker
==================================================
Base URL: https://example.substack.com
Concurrency: 10
Max retries: 3
Input: Sitemap
Year: 2024
==================================================

Found 45 posts from 2024
[1/45] Processing: https://example.substack.com/p/my-first-post
  Checking 12 links (10 new, 2 cached)...
  Found 1 broken links in this post

[2/45] Processing: https://example.substack.com/p/another-post
  Checking 8 links (6 new, 2 cached)...
  Found 0 broken links in this post
...

Completed in 34.2 seconds

==================================================
SUMMARY
==================================================
Total links checked: 234
Links skipped (assumed OK): 8
Links auto-flagged broken: 0
Cache hits: 45
Retries performed: 3
Broken links found: 5

Generating report: broken_links_report.csv
Report generated with 5 broken links
```

## CLI Options

| Option | Short | Description |
|--------|-------|-------------|
| `--base-url` | `-b` | Your Substack URL (required) |
| `--year` | `-y` | Year to check (uses sitemap) |
| `--url-file` | `-f` | File with post URLs (one per line) |
| `--output` | `-o` | Output CSV filename (default: broken_links_report.csv) |
| `--concurrency` | `-c` | Parallel requests (default: 10) |
| `--timeout` | `-t` | Request timeout in seconds (default: 10) |
| `--max-retries` | `-r` | Retry attempts for failures (default: 3) |
| `--history-file` | `-H` | JSON file for tracking checked posts |
| `--only-new` | | Only check posts not in history |
| `--skip-domains` | `-S` | Domains to skip (assumed OK) |
| `--skip-domains-file` | | File with domains to skip (one per line) |
| `--broken-domains` | `-B` | Domains to auto-flag as broken |
| `--broken-domains-file` | | File with domains to auto-flag (one per line) |
| `--cookie` | `-C` | Substack session cookie for authentication |
| `--verbose` | `-v` | Show detailed progress |
| `--limit` | `-l` | Max posts to check |

## Helper Scripts

| Script | Purpose |
|--------|---------|
| `compare_posts.py` | Find posts not yet checked (sitemap vs history) |
| `import_checked_posts.py` | Import previous results from Excel/CSV |
| `fetch_archive_urls.py` | Extract URLs from archive page (fallback) |
| `run_link_checker.ps1` | Windows Task Scheduler automation |
| `demo_link_checker.py` | Test the checker with sample URLs |

## Output

The tool generates a CSV report with columns:
- **Post Title**: Title of the post containing the broken link
- **Post URL**: URL of the post
- **Broken Link**: The broken URL
- **Error Type**: What went wrong (HTTP 404, DNS Failure, SSL Error, etc.)

## Error Types Detected

- `HTTP 404` - Page not found
- `HTTP 4xx/5xx` - Other HTTP errors
- `Soft 404` - Page loads but title indicates error
- `DNS Failure` - Domain doesn't exist
- `SSL Error` - Certificate problems
- `Timeout` - Server didn't respond
- `Connection Error` - Network issues
- `Known broken domain` - Auto-flagged via `--broken-domains`

## License

MIT License - see [LICENSE](LICENSE) file.

## Contributing

Issues and pull requests welcome at [github.com/jcddc83/substack-link-checker](https://github.com/jcddc83/substack-link-checker).
