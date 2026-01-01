# Detailed Usage Guide

This guide covers common workflows for checking broken links in your Substack newsletter.

## Getting Your Post URLs

The tool needs to know which posts to check. There are several ways to provide them:

### Option 1: Use the Sitemap (Easiest)

Substack automatically generates a sitemap with all your posts. Just specify the year:

```bash
python substack_link_checker.py --base-url https://YOUR.substack.com --year 2024
```

This fetches `https://YOUR.substack.com/sitemap.xml` and extracts all post URLs from that year.

### Option 2: Check All Posts via Sitemap

Omit the year to check everything (may take a while for large archives):

```bash
# First, get all post URLs from sitemap
python compare_posts.py https://YOUR.substack.com
# This creates unchecked_posts.txt with all posts

# Then check them
python substack_link_checker.py --base-url https://YOUR.substack.com \
    --url-file unchecked_posts.txt
```

### Option 3: Manual URL File

Create a text file with one post URL per line:

```text
https://YOUR.substack.com/p/my-first-post
https://YOUR.substack.com/p/second-post
https://YOUR.substack.com/p/third-post
```

Then run:
```bash
python substack_link_checker.py --base-url https://YOUR.substack.com --url-file posts.txt
```

## Recommended Workflow: Incremental Scanning

For ongoing maintenance, track which posts you've already checked:

### Initial Setup

```bash
# First run: check all posts from 2024, save history
python substack_link_checker.py --base-url https://YOUR.substack.com --year 2024 \
    --history-file checked_posts.json
```

### Monthly Check (New Posts Only)

```bash
# Find new posts not in history
python compare_posts.py https://YOUR.substack.com checked_posts.json

# Check only the new ones
python substack_link_checker.py --base-url https://YOUR.substack.com \
    --url-file unchecked_posts.txt \
    --history-file checked_posts.json \
    --only-new
```

### Automated Monthly Checks (Windows)

Use the PowerShell script with Task Scheduler:

1. Edit `run_link_checker.ps1` and set your Substack URL and paths
2. Open Task Scheduler
3. Create a new task that runs monthly
4. Action: Start a program
   - Program: `powershell.exe`
   - Arguments: `-ExecutionPolicy Bypass -File "C:\path\to\run_link_checker.ps1"`

## Authentication

If Substack blocks your requests or you need to access paywalled content, authenticate using your session cookie:

### Getting Your Cookie

1. Log into your Substack in a browser
2. Open Developer Tools (F12)
3. Go to **Application** → **Cookies** → your Substack domain
4. Find `substack.sid` and copy its value

### Using the Cookie

```bash
python substack_link_checker.py --base-url https://YOUR.substack.com --year 2024 \
    --cookie "your-long-cookie-value-here"
```

The cookie authenticates you as a logged-in user, bypassing bot protection.

## Domain Filtering

### Skipping Bot-Blocking Sites

Some sites (like Wikipedia) block automated requests. Skip them to avoid false positives:

```bash
python substack_link_checker.py ... --skip-domains wikipedia.org
```

These links are assumed OK and not checked. Default: `wikipedia.org`

To check all domains:
```bash
python substack_link_checker.py ... --skip-domains none
```

### Auto-Flagging Known Broken Domains

If you know certain domains are always broken (e.g., defunct sites), flag them automatically:

```bash
python substack_link_checker.py ... --broken-domains old.defunct-site.com local.test.com
```

These links appear in the report as "Known broken domain" without being checked.

## Importing Previous Results

If you have results from previous runs in Excel or CSV format:

```bash
# Import from Excel
python import_checked_posts.py broken_links_nov.xlsx --history-file checked_posts.json

# Import from CSV
python import_checked_posts.py broken_links_nov.csv --history-file checked_posts.json
```

This adds the post URLs to your history so they won't be re-checked.

## Performance Tuning

### Concurrency

Increase parallel requests for faster checking (be polite to servers):

```bash
# Default is 10 concurrent requests
python substack_link_checker.py ... --concurrency 20
```

### Timeout

Increase timeout for slow sites:

```bash
# Default is 10 seconds
python substack_link_checker.py ... --timeout 30
```

### Limiting Posts

Test with a small batch first:

```bash
python substack_link_checker.py ... --limit 5 --verbose
```

## Understanding the Output

### Console Summary

```
==================================================
SUMMARY
==================================================
Total links checked: 245
Links skipped (assumed OK): 12
Links auto-flagged broken: 3
Cache hits: 45
Retries performed: 8
Broken links found: 7
```

- **Total links checked**: Unique links that were actually tested
- **Links skipped**: Skipped due to `--skip-domains`
- **Links auto-flagged**: Flagged due to `--broken-domains`
- **Cache hits**: Links seen in multiple posts (checked once)
- **Retries**: Retry attempts for transient failures
- **Broken links found**: Total broken links in report

### CSV Report Columns

| Column | Description |
|--------|-------------|
| Post Title | Title of the post containing the link |
| Post URL | URL of the post |
| Broken Link | The broken URL |
| Error Type | HTTP 404, DNS Failure, SSL Error, Timeout, etc. |

## Troubleshooting

### "No posts found"

- Check your `--base-url` is correct (include https://)
- Try fetching the sitemap manually: `curl https://YOUR.substack.com/sitemap.xml`

### High number of broken links

- Some sites block automated requests → use `--skip-domains`
- Try increasing `--timeout` for slow sites
- Check with `--verbose` to see what's happening

### Script is slow

- Increase `--concurrency` (default: 10)
- Use `--history-file` with `--only-new` to skip already-checked posts

### SSL errors for valid sites

- Some sites have certificate issues that browsers ignore
- These are legitimate errors worth investigating
