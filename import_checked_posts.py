#!/usr/bin/env python3
"""
Import previously checked posts from Excel/CSV into checked_posts.json history.

Supports Excel (.xlsx) or CSV files with columns:
- Post Title, Post URL, Broken Link, Error Type

Extracts unique Post URLs and adds them to the history file.
"""

import argparse
import json
import os
import sys
from datetime import datetime

def load_existing_history(history_file):
    """Load existing history file if it exists."""
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('checked_posts', {})
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load existing history: {e}")
    return {}


def import_from_excel(excel_file):
    """Import post URLs from Excel file."""
    try:
        import pandas as pd
    except ImportError:
        print("Error: pandas is required for Excel import.")
        print("Install with: pip install pandas openpyxl")
        sys.exit(1)

    print(f"Reading Excel file: {excel_file}")
    df = pd.read_excel(excel_file)

    # Find the Post URL column (case-insensitive)
    url_column = None
    for col in df.columns:
        if 'post url' in col.lower() or 'post_url' in col.lower():
            url_column = col
            break

    if url_column is None:
        print(f"Error: Could not find 'Post URL' column. Found columns: {list(df.columns)}")
        sys.exit(1)

    # Extract unique URLs
    urls = df[url_column].dropna().unique().tolist()
    print(f"Found {len(urls)} unique post URLs")
    return urls


def import_from_csv(csv_file):
    """Import post URLs from CSV file."""
    import csv

    print(f"Reading CSV file: {csv_file}")
    urls = set()

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        # Find the Post URL column (case-insensitive)
        url_column = None
        for col in reader.fieldnames:
            if 'post url' in col.lower() or 'post_url' in col.lower():
                url_column = col
                break

        if url_column is None:
            print(f"Error: Could not find 'Post URL' column. Found columns: {reader.fieldnames}")
            sys.exit(1)

        for row in reader:
            url = row.get(url_column, '').strip()
            if url and url.startswith('http'):
                urls.add(url)

    print(f"Found {len(urls)} unique post URLs")
    return list(urls)


def save_history(history_file, checked_posts):
    """Save updated history to file."""
    data = {
        'last_updated': datetime.now().isoformat(),
        'checked_posts': checked_posts
    }
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Saved history with {len(checked_posts)} checked posts to {history_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Import checked posts from Excel/CSV into history file.'
    )
    parser.add_argument(
        'input_file',
        help='Excel (.xlsx) or CSV file with Post URL column'
    )
    parser.add_argument(
        '--history-file', '-H',
        default='checked_posts.json',
        help='History file to update (default: checked_posts.json)'
    )
    parser.add_argument(
        '--date',
        default=datetime.now().strftime('%Y-%m-%dT00:00:00'),
        help='Date to use for imported posts (default: today)'
    )

    args = parser.parse_args()

    # Load existing history
    checked_posts = load_existing_history(args.history_file)
    existing_count = len(checked_posts)
    print(f"Existing history: {existing_count} posts")

    # Import from file
    if args.input_file.endswith('.xlsx') or args.input_file.endswith('.xls'):
        urls = import_from_excel(args.input_file)
    elif args.input_file.endswith('.csv'):
        urls = import_from_csv(args.input_file)
    else:
        print("Error: File must be .xlsx, .xls, or .csv")
        sys.exit(1)

    # Add to history
    new_count = 0
    for url in urls:
        if url not in checked_posts:
            checked_posts[url] = args.date
            new_count += 1

    print(f"Added {new_count} new posts to history")
    print(f"Skipped {len(urls) - new_count} already in history")

    # Save updated history
    save_history(args.history_file, checked_posts)


if __name__ == '__main__':
    main()
