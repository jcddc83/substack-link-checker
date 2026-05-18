# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `pyproject.toml` making the project pip-installable with a
  `substack-link-checker` console entry point.
- GitHub Actions CI workflow (`.github/workflows/ci.yml`) running ruff
  lint, multi-version Python smoke tests, and a build step.
- `SECURITY.md` documenting vulnerability reporting and safe handling of
  Substack session cookies.
- `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md`.
- Issue and pull request templates under `.github/`.
- Dependabot configuration for weekly dependency and Actions updates.
- `.env.example` documenting the supported environment variables.

### Fixed
- Corrected the clone URL in `README.md` (was `substack-link-checker`,
  now `substack-broken-link-checker`).

## [0.1.0] - 2026-05-18

Initial public release.
