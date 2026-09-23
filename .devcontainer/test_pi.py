#!/usr/bin/env python
"""Offline checks for budget reporting and the settings shared with Pi."""

import hashlib
import json
import sys

import httpx
import pi
import pytest


@pytest.fixture
def env_file(tmp_path, monkeypatch):
    path = tmp_path / ".env"
    path.write_text("key=sk-test-only\n", encoding="utf-8")
    monkeypatch.setattr(pi, "ENV_FILE", path)
    return path


@pytest.mark.parametrize(
    ("limit", "spend", "expected"),
    [
        (20, 15, "25.0 % coding budget verbleibend"),
        (20, 7.66, "61.7 % coding budget verbleibend"),
        (20, 0, "100.0 % coding budget verbleibend"),
        (20, 20, "0.0 % coding budget verbleibend"),
        (0, 0, "0.0 % coding budget verbleibend"),
        (10, 12, "0.0 % coding budget verbleibend"),
        (None, 2, "Coding-Budget: kein eigenes Limit gesetzt"),
    ],
)
def test_key_budget(limit, spend, expected):
    assert pi.budget_summary({"spend": spend, "max_budget": limit}) == expected


@pytest.mark.parametrize(
    "info",
    [
        None,
        {},
        {"spend": 1},
        {"spend": None, "max_budget": None},
        {"spend": "2", "max_budget": 10},
        {"spend": -1, "max_budget": 10},
        {"spend": 1, "max_budget": -1},
        {"spend": float("nan"), "max_budget": 10},
        {"spend": 1, "max_budget": float("inf")},
        {"spend": True, "max_budget": 10},
    ],
)
def test_invalid_budget_is_not_reported_as_available(info):
    with pytest.raises(ValueError):
        pi.budget_summary(info)


def test_reset_and_blocked_key():
    result = pi.budget_summary(
        {
            "spend": 1,
            "max_budget": 10,
            "blocked": True,
            "budget_reset_at": "2026-10-01T00:00:00Z",
        }
    )
    assert result == "90.0 % coding budget verbleibend (API-Schluessel gesperrt)"


@pytest.mark.parametrize("suffix", ["", "/", "/v1", "/v1/chat/completions/"])
def test_budget_uses_pi_settings_without_exposing_key(
    env_file, monkeypatch, capsys, suffix
):
    # BOM, uppercase names and literal shell/interpolation characters are data.
    key = "sk-test-${SECRET}-$(echo-test)"
    env_file.write_text(
        f'KEY="{key}"\nURL=https://example.org/proxy{suffix}\nLLM=test-model\n',
        encoding="utf-8-sig",
    )

    def get(url, **kwargs):
        assert url == "https://example.org/proxy/key/info"
        assert kwargs["params"] == {"key": hashlib.sha256(key.encode()).hexdigest()}
        assert kwargs["headers"] == {"Authorization": f"Bearer {key}"}
        assert kwargs["follow_redirects"] is False
        assert kwargs["timeout"] == 15
        return httpx.Response(200, json={"info": {"spend": 7.66, "max_budget": 20}})

    monkeypatch.setattr(pi.httpx, "get", get)
    monkeypatch.setattr(sys, "argv", ["pi", "--budget"])
    monkeypatch.setattr(
        pi, "configure", lambda: pytest.fail("Budget must be read-only")
    )
    assert pi.main() == 0
    captured = capsys.readouterr()
    assert captured.out == "61.7 % coding budget verbleibend\n"
    assert key not in captured.out + captured.err


@pytest.mark.parametrize("status", [301, 401, 403, 404, 429, 500])
def test_http_failure_hides_response_and_credentials(
    env_file, monkeypatch, capsys, status
):
    monkeypatch.setattr(
        pi.httpx,
        "get",
        lambda *args, **kwargs: httpx.Response(status, text="SECRET sk-test-only"),
    )
    assert pi.show_budget() == 1
    captured = capsys.readouterr()
    assert not captured.out
    assert f"HTTP {status}" in captured.err
    assert "SECRET" not in captured.err and "sk-test-only" not in captured.err
    if status == 403:
        assert "/key/info" in captured.err


@pytest.mark.parametrize("body", ["not json", "[]", '{"info":{"spend":1}}'])
def test_invalid_success_response(env_file, monkeypatch, capsys, body):
    monkeypatch.setattr(
        pi.httpx,
        "get",
        lambda *args, **kwargs: httpx.Response(200, text=body),
    )
    assert pi.show_budget() == 1
    assert "keine gueltigen Budgetdaten" in capsys.readouterr().err


def test_timeout_hides_exception_details(env_file, monkeypatch, capsys):
    def get(*args, **kwargs):
        raise httpx.ReadTimeout("SECRET sk-test-only")

    monkeypatch.setattr(pi.httpx, "get", get)
    assert pi.show_budget() == 1
    captured = capsys.readouterr()
    assert "nicht erreichbar" in captured.err
    assert "sk-test-only" not in captured.err


def test_invalid_url_hides_exception_details(env_file, monkeypatch, capsys):
    def get(*args, **kwargs):
        raise httpx.InvalidURL("SECRET sk-test-only")

    monkeypatch.setattr(pi.httpx, "get", get)
    assert pi.show_budget() == 1
    captured = capsys.readouterr()
    assert "HTTPS-url" in captured.err
    assert "sk-test-only" not in captured.err


@pytest.mark.parametrize(
    "contents",
    [None, "key=\n", "key=DEIN_API_SCHLUESSEL\n", "key=test\nurl=http://example.org"],
)
def test_invalid_settings_never_make_a_request(env_file, monkeypatch, capsys, contents):
    if contents is None:
        env_file.unlink()
    else:
        env_file.write_text(contents)
    monkeypatch.setattr(
        pi.httpx,
        "get",
        lambda *args, **kwargs: pytest.fail("Unexpected request"),
    )
    assert pi.show_budget() == 1
    assert ".env" in capsys.readouterr().err
    assert env_file.exists() == (contents is not None)


def test_pi_configuration_still_uses_shared_settings(env_file, tmp_path, monkeypatch):
    monkeypatch.setattr(pi.Path, "home", lambda: tmp_path)
    monkeypatch.setenv("LITELLM_API_KEY", "")
    monkeypatch.setenv("PI_CODING_AGENT_DIR", "")
    assert pi.configure() is True
    models = json.loads((tmp_path / ".pi/agent/models.json").read_text())
    provider = models["providers"]["litellm"]
    assert provider["baseUrl"] == pi.LLM_URL + "/v1"
    assert provider["apiKey"] == "$LITELLM_API_KEY"
    assert pi.os.environ["LITELLM_API_KEY"] == "sk-test-only"
    assert "sk-test-only" not in json.dumps(models)
