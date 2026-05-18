# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `pyproject.toml` making the project pip-installable with a
  `substack-link-checker` console entry point.
- GitHub Actions CI workflow (`.github/workflows/ci.yml`) running ruff
  lint, multi-version Python smoke tests, a real `pytest` suite, and a
  build step.
- Initial `pytest` test suite (`tests/`) covering domain filtering,
  CSV report generation, history persistence, the
  `load_domains_from_file` helper, and cookie-handling guarantees.
- `SECURITY.md` documenting vulnerability reporting and safe handling of
  Substack session cookies.
- `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md`.
- Issue and pull request templates under `.github/`.
- Dependabot configuration for weekly dependency and Actions updates.
- `.env.example` documenting the supported environment variables.
- Release automation workflow (`.github/workflows/release.yml`): on
  pushing a `v*.*.*` tag, builds the sdist and wheel from
  `pyproject.toml` and attaches them to the GitHub Release. Verifies the
  tag matches the project version to prevent mismatched artifacts.

### Security
- `SUBSTACK_COOKIE` environment variable is now supported as a safer
  alternative to the `--cookie` CLI flag (which leaks the cookie into
  shell history and `ps aux`). README and `SECURITY.md` updated to
  recommend the env-var path.

### Fixed
- Corrected the clone URL in `README.md` (was `substack-link-checker`,
  now `substack-broken-link-checker`).

## [1.0.0] - 2026-01-01

Major rewrite of the Substack broken link checker with significant
performance improvements and new features. See the
[GitHub Release](https://github.com/jcddc83/substack-broken-link-checker/releases/tag/v1.0.0)
for the full announcement.

### Added
- Async concurrent link checking with `aiohttp` (10-20x faster than
  sequential).
- Smart link caching — the same URL across multiple posts is checked once.
- Retry logic with exponential backoff for transient failures.
- Incremental scanning: `--history-file` to track checked posts and
  `--only-new` to skip ones already covered.
- `import_checked_posts.py` to import previous results from Excel/CSV.
- Domain filtering: `--skip-domains` / `--skip-domains-file` to assume OK
  for bot-blocking sites; `--broken-domains` / `--broken-domains-file` to
  auto-flag known broken domains.
- `--cookie` flag for Substack session cookie authentication (works with
  paywalled / bot-protected content).
- Helper scripts: `compare_posts.py` to find unchecked posts,
  `fetch_archive_urls.py` as an archive-page fallback, and
  `run_link_checker.ps1` for Windows Task Scheduler automation.
- Complete `README.md` / `USAGE.md` rewrite with security considerations
  and expanded troubleshooting.

[Unreleased]: https://github.com/jcddc83/substack-broken-link-checker/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/jcddc83/substack-broken-link-checker/releases/tag/v1.0.0
