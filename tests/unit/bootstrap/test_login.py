"""Unit coverage for the canonical login bootstrap entrypoint."""

from __future__ import annotations

from pathlib import Path

import pytest
from telethon.errors import RPCError

from telegram_aggregator.bootstrap.login import run_login


def test_run_login_authorizes_interactively(
    set_service_env,
    fake_telethon_client_cls,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    set_service_env()
    fake_client = fake_telethon_client_cls()
    prompts = iter(["+380501234567", "12345"])

    monkeypatch.setattr("builtins.input", lambda prompt: next(prompts))
    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.getpass.getpass",
        lambda prompt: "secret-password",
    )

    def _build_client(**kwargs):
        fake_client.kwargs = kwargs
        return fake_client

    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.telethon.TelegramClient",
        _build_client,
    )

    run_login()

    assert fake_client.kwargs == {
        "session": str((tmp_path / "sessions/default.session").resolve()),
        "api_id": 123,
        "api_hash": "hash",
    }
    assert fake_client.start_calls == 1
    assert fake_client.prompt_values == {
        "phone": "+380501234567",
        "code": "12345",
        "password": "secret-password",
    }
    assert fake_client.disconnect_calls == 1


def test_run_login_creates_missing_session_parent_directory(
    set_service_env,
    fake_telethon_client_cls,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    set_service_env(session_path="nested/sessions/default.session")
    fake_client = fake_telethon_client_cls(start_uses_prompts=False)

    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.telethon.TelegramClient",
        lambda **kwargs: fake_client,
    )

    run_login()

    assert (tmp_path / "nested/sessions").is_dir()


def test_run_login_is_idempotent_for_existing_authorized_session(
    set_service_env,
    fake_telethon_client_cls,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env(create_session_file=True)
    fake_client = fake_telethon_client_cls(start_uses_prompts=False)

    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.telethon.TelegramClient",
        lambda **kwargs: fake_client,
    )

    run_login()

    assert fake_client.start_calls == 1
    assert fake_client.prompt_values == {}
    assert fake_client.disconnect_calls == 1


def test_run_login_respects_dry_run_contract(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env()
    monkeypatch.setenv("DRY_RUN", "1")
    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.telethon.TelegramClient",
        lambda **kwargs: (_ for _ in ()).throw(
            AssertionError("Telethon must not be touched in DRY_RUN")
        ),
    )

    with pytest.raises(
        SystemExit,
        match="Login bootstrap is disabled when DRY_RUN is enabled",
    ):
        run_login()


def test_run_login_surfaces_canonical_loader_errors(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env()
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(SystemExit, match="Missing required environment variable: DATABASE_URL"):
        run_login()


def test_run_login_surfaces_session_path_errors(
    set_service_env,
    tmp_path: Path,
) -> None:
    session_dir = tmp_path / "session-dir"
    session_dir.mkdir()
    set_service_env(session_path="session-dir")

    with pytest.raises(
        SystemExit,
        match="Session path must point to a file, not a directory:",
    ):
        run_login()


def test_run_login_surfaces_authorization_failures(
    set_service_env,
    fake_telethon_client_cls,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env()
    fake_client = fake_telethon_client_cls(
        start_exception=RPCError(request=None, message="AUTH_FAIL", code=400)
    )

    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.telethon.TelegramClient",
        lambda **kwargs: fake_client,
    )

    with pytest.raises(
        SystemExit,
        match="Telegram authorization failed: RPCError 400: AUTH_FAIL",
    ):
        run_login()


def test_run_login_surfaces_unexpected_errors_as_clean_exit(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env()

    monkeypatch.setattr(
        "telegram_aggregator.telegram.client.telethon.TelegramClient",
        lambda **kwargs: (_ for _ in ()).throw(
            OSError("network is unreachable")
        ),
    )

    with pytest.raises(
        SystemExit,
        match="Telegram session path is not usable: .*network is unreachable",
    ):
        run_login()
