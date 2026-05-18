# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it
privately rather than opening a public issue.

- Preferred: use GitHub's [private vulnerability reporting](https://github.com/jcddc83/substack-broken-link-checker/security/advisories/new).
- Alternatively, open a minimal public issue requesting a private contact channel — do not include exploit details.

Please include:

- A description of the issue and its impact
- Steps to reproduce
- Affected versions / commit
- Any suggested mitigation

You can expect an initial response within 7 days.

## Supported Versions

Only the latest release on `main` receives security fixes.

## Handling Session Cookies

This tool accepts a Substack session cookie (`substack.sid`) via the
`--cookie` flag in order to access bot-protected or paywalled posts.
**Treat this value like a password.**

Recommended practices:

- Do **not** commit cookies to source control or paste them into public
  logs, screenshots, or issue reports.
- Prefer passing the cookie via an environment variable or a local file
  ignored by `.gitignore` rather than your shell history.
- Rotate the cookie by logging out and back in if you suspect it was
  exposed. Substack session cookies typically expire after a few weeks.
- The tool sends the cookie only to the `--base-url` you specify. Verify
  that URL before running.

If you find the tool logging the cookie value to disk or transmitting it
to any host other than the configured Substack domain, please report it
through the channels above.

## Dependencies

Dependencies are pinned with minimum versions in `pyproject.toml` and
monitored via Dependabot (`.github/dependabot.yml`). Please update to the
latest release to pick up upstream security fixes.
