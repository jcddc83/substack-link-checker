"""Tests verifying safe cookie handling.

These tests pin down the SECURITY.md promises:
- The cookie is scoped to .substack.com on the requests session.
- The cookie value never appears in any logged output (verbose or not).
- The async outbound link-check session is constructed without cookies.
"""

from substack_link_checker import SubstackLinkChecker

COOKIE_SENTINEL = "s%3Asentinelcookievalue1234567890.signaturepart"


def test_cookie_set_on_requests_session_with_substack_domain():
    checker = SubstackLinkChecker(
        base_url="https://example.substack.com",
        cookie=COOKIE_SENTINEL,
    )
    jar = checker.session.cookies
    matching = [c for c in jar if c.name == "substack.sid"]
    assert len(matching) == 1
    assert matching[0].value == COOKIE_SENTINEL
    assert matching[0].domain.endswith("substack.com")


def test_no_cookie_means_empty_jar():
    checker = SubstackLinkChecker(base_url="https://example.substack.com")
    assert [c for c in checker.session.cookies if c.name == "substack.sid"] == []


def test_cookie_not_emitted_by_log(capsys):
    """`_log` with verbose=True must never include the cookie value."""
    checker = SubstackLinkChecker(
        base_url="https://example.substack.com",
        verbose=True,
        cookie=COOKIE_SENTINEL,
    )
    checker._log("processing https://example.substack.com/p/one")
    checker._log("forced message", force=True)
    out = capsys.readouterr().out
    assert COOKIE_SENTINEL not in out


def test_cookie_not_emitted_when_saving_history(tmp_path):
    """History JSON must not leak the cookie."""
    checker = SubstackLinkChecker(
        base_url="https://example.substack.com",
        cookie=COOKIE_SENTINEL,
    )
    history = tmp_path / "history.json"
    checker.load_history(str(history))
    checker.mark_post_checked("https://example.substack.com/p/one")
    checker.save_history()
    assert COOKIE_SENTINEL not in history.read_text(encoding="utf-8")


def test_repr_does_not_leak_cookie():
    """The default repr of the checker should not expose the cookie."""
    checker = SubstackLinkChecker(
        base_url="https://example.substack.com",
        cookie=COOKIE_SENTINEL,
    )
    assert COOKIE_SENTINEL not in repr(checker)


def test_env_var_used_when_cli_flag_absent(monkeypatch, tmp_path):
    """The check CLI should read SUBSTACK_COOKIE when --cookie is not passed."""
    from substack_link_checker import _cli_check

    monkeypatch.setenv("SUBSTACK_COOKIE", COOKIE_SENTINEL)
    monkeypatch.setattr(
        "sys.argv",
        [
            "substack-link-checker check",
            "--base-url",
            "https://example.substack.com",
            "--url-file",
            str(tmp_path / "empty.txt"),
        ],
    )
    (tmp_path / "empty.txt").write_text("")

    captured = {}

    class FakeChecker:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        def run(self, **kwargs):
            pass

    monkeypatch.setattr(_cli_check, "SubstackLinkChecker", FakeChecker)
    _cli_check.main()

    assert captured["cookie"] == COOKIE_SENTINEL


def test_cli_flag_overrides_env_var(monkeypatch, tmp_path):
    from substack_link_checker import _cli_check

    monkeypatch.setenv("SUBSTACK_COOKIE", "env-value")
    monkeypatch.setattr(
        "sys.argv",
        [
            "substack-link-checker check",
            "--base-url",
            "https://example.substack.com",
            "--url-file",
            str(tmp_path / "empty.txt"),
            "--cookie",
            "cli-value",
        ],
    )
    (tmp_path / "empty.txt").write_text("")

    captured = {}

    class FakeChecker:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        def run(self, **kwargs):
            pass

    monkeypatch.setattr(_cli_check, "SubstackLinkChecker", FakeChecker)
    _cli_check.main()

    assert captured["cookie"] == "cli-value"
