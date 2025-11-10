# Substack Broken Link Checker - Usage Guide

## Overview

This tool checks links from your Substack newsletter archive and generates a CSV report of broken links with detailed error information.

## Installation

```bash
pip install -r requirements.txt
```

## Bypassing Bot Protection (RECOMMENDED)

Substack uses bot protection that may block automated requests. The best way to bypass this is to use **cookie-based authentication** from a logged-in session:

### Getting Your Session Cookie

1. **Log into Substack** in your browser (any Substack site)
2. **Visit your Substack page** (e.g., https://yoursubstack.substack.com)
3. **Open DevTools** (Press F12 or right-click → Inspect)
4. **Go to the Application/Storage tab**
   - Chrome/Edge/Vivaldi: Application → Cookies
   - Firefox: Storage → Cookies
5. **Click on your Substack domain** in the left sidebar under Cookies
6. **Find the `substack.sid` cookie** and copy its value
   - Look for the cookie under your Substack domain (e.g., https://yoursubstack.substack.com)
   - Copy the entire value (long string of characters)

### Using the Cookie

```python
from substack_link_checker import SubstackLinkChecker

# Initialize with your session cookie
cookie = 'your-substack-sid-value-here'  # Paste your substack.sid cookie value
checker = SubstackLinkChecker(
    'https://yoursubstack.substack.com',
    use_playwright=False,
    cookie=cookie
)

# Now run the checker - it will use authenticated requests
checker.run(
    url_file='post_urls_2020.txt',
    limit=10,
    output_file='broken_links_2020.csv'
)
```

**Note**: Your session cookie will eventually expire (usually after a few weeks). If you start getting 403 errors again, get a fresh cookie from your browser.

## Quick Start

### Step 1: Get Post URLs

Since your Substack site (https://yoursubstack.substack.com) has anti-bot protection, you'll need to manually collect post URLs:

1. **Visit the archive page** in your browser:
   - Go to: https://yoursubstack.substack.com/archive

2. **Copy post URLs from 2020**:
   - Right-click on each post link and copy the URL
   - URLs should look like: `https://yoursubstack.substack.com/p/post-title-here`

3. **Save URLs to a text file** (e.g., `post_urls_2020.txt`):
   ```
   https://yoursubstack.substack.com/p/first-post-title
   https://yoursubstack.substack.com/p/second-post-title
   https://yoursubstack.substack.com/p/third-post-title
   ```
   - One URL per line
   - Lines starting with `#` are treated as comments

4. **Start with 10 posts** for initial testing

### Step 2: Run the Link Checker

#### Option A: Using the command line

Edit `substack_link_checker.py` and update the `main()` function:

```python
def main():
    checker = SubstackLinkChecker('https://yoursubstack.substack.com')
    checker.run(
        url_file='post_urls_2020.txt',
        limit=10,
        output_file='broken_links_2020_sample.csv'
    )
```

Then run:
```bash
python substack_link_checker.py
```

#### Option B: Using Python interactively

```python
from substack_link_checker import SubstackLinkChecker

# Initialize the checker
checker = SubstackLinkChecker('https://yoursubstack.substack.com')

# Run on 10 posts from your URL file
checker.run(
    url_file='post_urls_2020.txt',
    limit=10,
    output_file='broken_links_2020_sample.csv'
)

# Or run on all URLs in the file
checker.run(
    url_file='post_urls_2020.txt',
    limit=None,
    output_file='broken_links_2020_full.csv'
)
```

### Step 3: Review the Report

The script will generate a CSV file (e.g., `broken_links_2020_sample.csv`) with these columns:

| Column | Description |
|--------|-------------|
| `post_title` | Title of the Substack post |
| `post_url` | URL of the post containing the broken link |
| `broken_link` | The broken URL |
| `error_type` | Type of error detected |

## Error Types Detected

The tool detects various types of broken links:

1. **HTTP 404**: Standard "Not Found" responses
2. **HTTP 4xx/5xx**: Other error status codes (400, 403, 500, etc.)
3. **SSL Errors**: Certificate or HTTPS connection issues
4. **SSL Error (local.theonion.com)**: Known issue with local.theonion.com links
5. **Timeout**: Request took longer than 10 seconds
6. **DNS Failure**: Domain name could not be resolved
7. **Connection Error**: Network connection failed
8. **Soft 404**: Page loads (200 OK) but title contains "404" or "not found"

## Advanced Usage

### Check Multiple Years

```python
checker = SubstackLinkChecker('https://yoursubstack.substack.com')

# Check 2020
checker.run(url_file='post_urls_2020.txt', output_file='broken_2020.csv')

# Reset results for next year
checker.results = []

# Check 2021
checker.run(url_file='post_urls_2021.txt', output_file='broken_2021.csv')
```

### Adjust Timeout

```python
# Increase timeout to 30 seconds for slow links
checker = SubstackLinkChecker('https://yoursubstack.substack.com', timeout=30)
```

### Custom Link Filtering

To modify which links are checked, edit the `extract_links_from_post` method in `substack_link_checker.py`:

```python
# Skip specific domains
if 'example.com' in link:
    continue

# Only check specific domains
if not any(domain in link for domain in ['theonion.com', 'nytimes.com']):
    continue
```

## Workflow for Full Archive

1. **Test first** with 10 posts to validate everything works
2. **Collect all URLs** for the target year
3. **Run in batches** if you have many posts (e.g., 50 at a time)
4. **Review results** and investigate high-priority broken links
5. **Repeat** for other years as needed

## Troubleshooting

### "No broken links found" but I know there are broken links

- Check that your URL file contains valid post URLs
- Verify the posts actually have external links
- Try increasing the timeout value

### Script is very slow

- This is normal! The script intentionally waits 0.5 seconds between each link check to be polite to servers
- Checking 10 posts with 20 links each = ~100 seconds minimum
- You can reduce the delay by editing line 248: `time.sleep(0.5)` → `time.sleep(0.2)`

### Too many false positives

Some sites may block automated requests. You can:
- Manually verify suspected broken links in your browser
- Add domains to a skip list in the code
- Adjust the soft 404 detection logic

## Output Example

```csv
post_title,post_url,broken_link,error_type
"My First Post",https://yoursubstack.substack.com/p/first-post,https://example.com/dead-link,HTTP 404
"My First Post",https://yoursubstack.substack.com/p/first-post,https://local.theonion.com/article,SSL Error (local.theonion.com)
"Another Post",https://yoursubstack.substack.com/p/another-post,https://oldsite.com/page,DNS Failure
```

## Helper Scripts

### `fetch_archive_urls.py`

Attempts to automatically fetch post URLs from the archive page:

```bash
python fetch_archive_urls.py 2020
```

**Note**: This likely won't work due to anti-bot protection, but it's worth trying. If it fails, collect URLs manually as described above.

### `demo_link_checker.py`

Tests the link checking logic on example URLs:

```bash
python demo_link_checker.py
```

## Next Steps

Once you've validated the approach with 10 posts:

1. Collect all 2020 post URLs
2. Run the full check: `checker.run(url_file='post_urls_2020.txt', limit=None)`
3. Review the generated CSV report
4. Repeat for other years (2021, 2022, etc.)

## Tips

- **Start small**: Always test with a few posts first
- **Be patient**: Link checking takes time (0.5s per link minimum)
- **Be respectful**: Don't reduce the delay too much or servers may block you
- **Verify manually**: Check a few broken links in your browser to confirm they're really broken
- **Regular runs**: Consider running this quarterly to catch new broken links

