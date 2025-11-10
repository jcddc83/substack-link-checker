#!/usr/bin/env python3
"""
Demo script to test the link checker on a few example links.
This demonstrates the link checking logic without needing full post URLs.
"""

from substack_link_checker import SubstackLinkChecker


def test_link_checker():
    """Test the link checker with various types of links."""

    checker = SubstackLinkChecker('https://yoursubstack.substack.com')

    # Test various link types
    test_links = [
        ('https://example.com', 'Working link (example.com)'),
        ('https://httpbin.org/status/404', 'HTTP 404 test'),
        ('https://thisdoesnotexist123456789xyzabc.com', 'DNS failure test'),
        ('https://local.theonion.com/something', 'local.theonion.com SSL error test'),
        ('https://httpbin.org/status/200', 'Working link (httpbin)'),
        ('https://httpbin.org/status/500', 'HTTP 500 error test'),
    ]

    print("Link Checker Test")
    print("=" * 70)

    for link, description in test_links:
        print(f"\nTesting: {description}")
        print(f"URL: {link}")

        is_broken, error_type = checker.check_link(link)

        if is_broken:
            print(f"Result: ✗ BROKEN - {error_type}")
        else:
            print(f"Result: ✓ OK")

    print("\n" + "=" * 70)


if __name__ == '__main__':
    test_link_checker()

