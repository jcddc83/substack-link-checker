# Contributing

Thanks for your interest in improving the Substack Broken Link Checker.

## Development setup

```bash
git clone https://github.com/jcddc83/substack-broken-link-checker.git
cd substack-broken-link-checker
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Before opening a PR

- Run the linter: `ruff check .`
- Run the formatter: `ruff format .`
- Run the tests: `pytest`
- Verify the CLI still launches: `python substack_link_checker.py --help`

## Filing issues

Please use the issue templates under `.github/ISSUE_TEMPLATE/`. For bugs,
include your Python version, OS, the command you ran (with the cookie
value redacted), and the full error output.

## Reporting security issues

See [SECURITY.md](SECURITY.md). Do **not** file public issues for security
vulnerabilities.

## Pull requests

- Keep PRs focused — one logical change per PR.
- Update the `README.md` and `USAGE.md` if you change CLI behavior.
- Add tests for new behavior where practical.
- Match the style of the surrounding code.

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).
