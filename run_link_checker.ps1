# Substack Link Checker - Scheduled Task Script
#
# This script checks for new posts and scans them for broken links.
# Set up with Windows Task Scheduler to run monthly.
#
# SETUP: Update the configuration variables below before first use.

# ============================================
# CONFIGURATION - Update these for your setup
# ============================================
$SUBSTACK_URL = "https://YOUR-SUBSTACK.substack.com"  # Your Substack URL
$PROJECT_DIR = "C:\path\to\substack-link-checker"      # Where you cloned this repo
# ============================================

Set-Location $PROJECT_DIR

# Create logs and reports directories if they don't exist
New-Item -ItemType Directory -Force -Path "logs" | Out-Null
New-Item -ItemType Directory -Force -Path "reports" | Out-Null

$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"

# Log output
Start-Transcript -Path "logs\run_$timestamp.log"

Write-Host "=========================================="
Write-Host "Substack Link Checker - Scheduled Run"
Write-Host "Started: $(Get-Date)"
Write-Host "Substack: $SUBSTACK_URL"
Write-Host "=========================================="

# Step 1: Compare sitemap against history to find new posts
Write-Host "`nStep 1: Finding new posts..."
python compare_posts.py $SUBSTACK_URL checked_posts.json

# Step 2: Check the unchecked posts (--only-new ensures we skip any already in history)
Write-Host "`nStep 2: Checking unchecked posts for broken links..."
python substack_link_checker.py --base-url $SUBSTACK_URL --url-file unchecked_posts.txt --history-file checked_posts.json --only-new --output "reports\broken_links_$timestamp.csv" --verbose

Write-Host "`n=========================================="
Write-Host "Completed: $(Get-Date)"
Write-Host "Report saved to: reports\broken_links_$timestamp.csv"
Write-Host "=========================================="

Stop-Transcript
