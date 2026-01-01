# Substack Link Checker - Monthly Scheduled Task
# This script checks for new posts and scans them for broken links

Set-Location "C:\Users\james\.claude\projects\substack-link-checker"

# Create logs and reports directories if they don't exist
New-Item -ItemType Directory -Force -Path "logs" | Out-Null
New-Item -ItemType Directory -Force -Path "reports" | Out-Null

$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"

# Log output
Start-Transcript -Path "logs\run_$timestamp.log"

Write-Host "=========================================="
Write-Host "Substack Link Checker - Scheduled Run"
Write-Host "Started: $(Get-Date)"
Write-Host "=========================================="

# Step 1: Compare sitemap against history to find new posts
Write-Host "`nStep 1: Finding new posts..."
python compare_posts.py https://onion20.substack.com checked_posts.json

# Step 2: Check the unchecked posts
Write-Host "`nStep 2: Checking unchecked posts for broken links..."
python substack_link_checker.py --base-url https://onion20.substack.com --url-file unchecked_posts.txt --history-file checked_posts.json --output "reports\broken_links_$timestamp.csv" --verbose

Write-Host "`n=========================================="
Write-Host "Completed: $(Get-Date)"
Write-Host "Report saved to: reports\broken_links_$timestamp.csv"
Write-Host "=========================================="

Stop-Transcript
