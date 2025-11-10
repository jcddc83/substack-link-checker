# Substack Broken Link Checker 
A Python tool to automatically check for broken links in your Substack newsletter archive and generate detailed reports with clickable hyperlinks. 
## Features 
- ✅ **Comprehensive Link Checking**: Detects HTTP 404s, SSL errors, DNS failures, timeouts, and soft 404s
- ✅ **Excel Reports with Hyperlinks**: Generates `.xlsx` files with clickable links (no more copy-pasting!)
- ✅ **Batch Processing**: Process large archives in manageable batches (25 posts at a time)
- ✅ **Bot Protection Bypass**: Uses authenticated sessions and cloudscraper to bypass anti-bot protection
- ✅ **Polite Crawling**: Built-in delays to respect server resources and avoid rate limiting
- ✅ **Detailed Error Reporting**: Know exactly why each link failed 
## Quick Start 
### 1. Installation 
```bash
# Clone the repository
git clone https://github.com/jcddc83/test.git
cd test 
# Install dependencies
pip install -r requirements.txt
``` 
### 2. Prepare Your URL List 
Create a text file (e.g., `post_urls_2020.txt`) with one Substack post URL per line: 
```
https://yoursubstack.substack.com/p/post-title-1
https://yoursubstack.substack.com/p/post-title-2
https://yoursubstack.substack.com/p/post-title-3
``` 
Visit your Substack archive page (e.g., `https://yoursubstack.substack.com/archive`) to find post URLs. 
### 3. Run the Checker 
**Process in batches (recommended for large archives):** 
```bash
# Check batch 1 (posts 0-24)
python substack_link_checker.py --batch 1 
# Check batch 6 (posts 125-149)
python substack_link_checker.py --batch 6 
# Check all remaining posts
python substack_link_checker.py --all
``` 
**Or check a specific number of posts:** 
```python
from substack_link_checker import SubstackLinkChecker 
checker = SubstackLinkChecker('https://yoursubstack.substack.com')
checker.run(
url_file='post_urls_2020.txt',
limit=10,
output_file='broken_links_sample.csv'
)
``` 
### 4. Review Results 
The script generates two report formats: 
**CSV File** (`broken_links_batch01.csv`):
```csv
post_title,post_url,broken_link,error_type
"My Post Title",https://...,https://broken-link.com,HTTP 404
``` 
**Excel File** (`broken_links_batch01.xlsx`):
- Clickable hyperlinks for all URLs (just click to open!)
- Styled headers
- Auto-adjusted column widths
- Easy to review and share 
## Command-Line Options 
```bash
# Run a specific batch (1-13, each batch = 25 posts)
python substack_link_checker.py --batch 6 
# Run all posts
python substack_link_checker.py --all 
# See help
python substack_link_checker.py --help
``` 
## Error Types Detected 
| Error Type | Description |
|------------|-------------|
| `HTTP 404` | Standard "Not Found" error |
| `HTTP 4xx/5xx` | Other HTTP errors (403, 500, etc.) |
| `SSL Error` | Certificate or HTTPS issues |
| `DNS Failure` | Domain name cannot be resolved |
| `Timeout` | Request took longer than timeout limit |
| `Connection Error` | Network connection failed |
| `Soft 404` | Page loads but title indicates error | 
## Advanced Usage 
### Bypass Bot Protection 
If you encounter 403 errors, use your authenticated session cookie: 
```python
checker = SubstackLinkChecker(
'https://yoursubstack.substack.com',
use_playwright=False,
cookie='your-substack-sid-cookie-value'
)
``` 
See [USAGE.md](USAGE.md) for detailed instructions on getting your session cookie. 
### Process Multiple Years 
```python
checker = SubstackLinkChecker('https://yoursubstack.substack.com') 
# Check 2020
checker.run(url_file='post_urls_2020.txt', output_file='broken_2020.csv') 
# Reset for next year
checker.results = [] 
# Check 2021
checker.run(url_file='post_urls_2021.txt', output_file='broken_2021.csv')
``` 
### Adjust Timeout 
```python
# For slower connections or sites
checker = SubstackLinkChecker('https://yoursubstack.substack.com', timeout=30)
``` 
## Requirements 
- Python 3.7+
- requests
- beautifulsoup4
- cloudscraper
- openpyxl (for Excel output)
- playwright (optional, for advanced bot bypass) 
See [requirements.txt](requirements.txt) for specific versions. 
## Documentation 
- [USAGE.md](USAGE.md) - Detailed usage guide with troubleshooting
- [demo_link_checker.py](demo_link_checker.py) - Test the link checking logic
- [fetch_archive_urls.py](fetch_archive_urls.py) - Helper to fetch URLs from archive 
## Use Cases 
- **Content audits**: Find and fix broken links in your newsletter archive
- **Migration prep**: Identify problematic links before migrating platforms
- **Quality assurance**: Regular checks to maintain content quality
- **Research**: Analyze link decay patterns in online content 
## Performance Notes 
- The script intentionally waits between requests (0.5-3 seconds) to be respectful to servers
- Checking 25 posts with ~10 links each takes approximately 5-10 minutes
- Processing time varies based on link count and response times 
## Contributing 
Contributions are welcome! Feel free to: 
- Report bugs via GitHub Issues
- Submit pull requests
- Suggest new features
- Improve documentation 
## License 
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 
## Acknowledgments 
This tool was developed to help Substack creators maintain high-quality archives by identifying and fixing broken links. Special thanks to the open-source community for the excellent libraries that made this possible. 
## Support 
If you find this tool useful, consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs or suggesting features
- 📢 Sharing with other Substack creators 
## Author 
Created by [@jcddc83](https://github.com/jcddc83) 
--- 
**Happy link checking!** 🔍✨
