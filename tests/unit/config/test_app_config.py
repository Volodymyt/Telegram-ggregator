"""Unit coverage for the canonical application config surface."""

from __future__ import annotations

from pathlib import Path

import pytest

from telegram_aggregator.config import (
    AppConfigError,
    ConfigPathError,
    ConfigSemanticError,
    IdentifierFormatError,
    load_app_config,
)


def test_load_app_config_resolves_relative_paths(set_service_env, tmp_path: Path) -> None:
    config_file = set_service_env()

    config = load_app_config()

    assert config.telegram.session_path == (tmp_path / "sessions/default.session").resolve()
    assert config.config_path == config_file.resolve()
    assert config.file_config.sources == ()
    assert config.file_config.filters[0].mode == "any"
    assert config.file_config.runtime.candidate_similarity_threshold == pytest.approx(0.82)
    assert config.log_level == "INFO"
    assert config.dry_run is False


def test_load_app_config_rejects_invalid_api_id(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env()
    monkeypatch.setenv("TG_API_ID", "not-an-int")

    with pytest.raises(
        AppConfigError,
        match="Environment variable TG_API_ID must be a valid integer",
    ):
        load_app_config()


def test_load_app_config_rejects_missing_database_url(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env()
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(
        AppConfigError,
        match="Missing required environment variable: DATABASE_URL",
    ):
        load_app_config()


def test_load_app_config_rejects_missing_config_file(set_service_env) -> None:
    set_service_env(config_path="missing.yaml")

    with pytest.raises(ConfigPathError, match="Config file does not exist:"):
        load_app_config()


def test_load_app_config_rejects_invalid_boolean(set_service_env) -> None:
    set_service_env(dry_run="sometimes")

    with pytest.raises(
        AppConfigError,
        match="Environment variable DRY_RUN must be a boolean value",
    ):
        load_app_config()


def test_load_app_config_rejects_invalid_log_level(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env()
    monkeypatch.setenv("LOG_LEVEL", "verbose")

    with pytest.raises(
        AppConfigError,
        match="Environment variable LOG_LEVEL must be one of:",
    ):
        load_app_config()


def test_load_app_config_allows_blank_telegram_values_in_dry_run(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env(dry_run="1")
    monkeypatch.setenv("TG_API_ID", "   ")
    monkeypatch.setenv("TG_API_HASH", "   ")
    monkeypatch.setenv("TARGET_CHANNEL", "   ")

    config = load_app_config()

    assert config.dry_run is True
    assert config.telegram.api_id is None
    assert config.telegram.api_hash == ""
    assert config.target_channel == ""


def test_load_app_config_still_rejects_blank_target_channel_outside_dry_run(
    set_service_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_service_env(dry_run="0")
    monkeypatch.setenv("TARGET_CHANNEL", "   ")

    with pytest.raises(
        AppConfigError,
        match="Environment variable TARGET_CHANNEL must not be empty",
    ):
        load_app_config()


@pytest.mark.parametrize(
    ("content", "message"),
    [
        (
            "case_insensitive",
            "Config field filters\\[0\\].case_insensitive must be a boolean",
        ),
        (
            "normalize",
            "Config field filters\\[0\\].normalize must be a boolean",
        ),
    ],
)
def test_load_app_config_rejects_non_boolean_filter_toggles(
    set_service_env,
    semantic_valid_config_yaml: str,
    content: str,
    message: str,
) -> None:
    replacement = (
        semantic_valid_config_yaml.replace(
            "    case_insensitive: true",
            '    case_insensitive: "yes"',
            1,
        )
        if content == "case_insensitive"
        else semantic_valid_config_yaml.replace(
            "    normalize: true",
            '    normalize: "yes"',
            1,
        )
    )

    set_service_env(config_content=replacement)

    with pytest.raises(AppConfigError, match=message):
        load_app_config()


def test_load_app_config_accepts_supported_identifier_forms(
    set_service_env,
    semantic_valid_config_yaml: str,
) -> None:
    set_service_env(
        config_content=semantic_valid_config_yaml,
        target_channel="alerts",
    )

    config = load_app_config()

    assert config.file_config.sources == (
        "@channel1",
        "https://t.me/channel2",
        "-1001234567890",
    )
    assert config.target_channel == "alerts"


def test_load_app_config_accepts_numeric_target_channel(
    set_service_env,
    semantic_valid_config_yaml: str,
) -> None:
    set_service_env(
        config_content=semantic_valid_config_yaml,
        target_channel="-100987654321",
    )

    config = load_app_config()

    assert config.target_channel == "-100987654321"


@pytest.mark.parametrize("target_channel", ["0", "-0", "+123"])
def test_load_app_config_rejects_invalid_numeric_target_channel(
    set_service_env,
    semantic_valid_config_yaml: str,
    target_channel: str,
) -> None:
    set_service_env(
        config_content=semantic_valid_config_yaml,
        target_channel=target_channel,
    )

    with pytest.raises(
        IdentifierFormatError,
        match="Environment variable TARGET_CHANNEL must be a Telegram target identifier in one of these forms: username, @username, or non-zero numeric id",
    ):
        load_app_config()


def test_load_app_config_rejects_target_channel_url(
    set_service_env,
    semantic_valid_config_yaml: str,
) -> None:
    set_service_env(
        config_content=semantic_valid_config_yaml,
        target_channel="https://t.me/alerts",
    )

    with pytest.raises(
        IdentifierFormatError,
        match="Environment variable TARGET_CHANNEL must use username, @username, or numeric id, not a Telegram URL",
    ):
        load_app_config()


def test_load_app_config_rejects_invalid_source_identifier(
    set_service_env,
    semantic_valid_config_yaml: str,
) -> None:
    set_service_env(
        config_content=semantic_valid_config_yaml.replace(
            '  - "@channel1"\n',
            '  - "channel1"\n',
            1,
        ),
    )

    with pytest.raises(
        IdentifierFormatError,
        match="Config field sources\\[0\\] must be a Telegram source identifier in one of these forms: @username, t\\.me/<username>, or non-zero numeric id",
    ):
        load_app_config()


@pytest.mark.parametrize("source_value", ["0", "-0", "+123"])
def test_load_app_config_rejects_invalid_numeric_source_identifier(
    set_service_env,
    semantic_valid_config_yaml: str,
    source_value: str,
) -> None:
    set_service_env(
        config_content=semantic_valid_config_yaml.replace(
            '  - "@channel1"\n',
            f'  - "{source_value}"\n',
            1,
        ),
    )

    with pytest.raises(
        IdentifierFormatError,
        match="Config field sources\\[0\\] must be a Telegram source identifier",
    ):
        load_app_config()


def test_load_app_config_rejects_source_identifier_with_whitespace(
    set_service_env,
    semantic_valid_config_yaml: str,
) -> None:
    set_service_env(
        config_content=semantic_valid_config_yaml.replace(
            '  - "@channel1"\n',
            '  - " @channel1 "\n',
            1,
        ),
    )

    with pytest.raises(
        IdentifierFormatError,
        match="Config field sources\\[0\\] must not contain leading or trailing whitespace",
    ):
        load_app_config()


def test_load_app_config_rejects_source_invite_link(
    set_service_env,
    semantic_valid_config_yaml: str,
) -> None:
    set_service_env(
        config_content=semantic_valid_config_yaml.replace(
            '  - "@channel1"\n',
            '  - "https://t.me/+invite"\n',
            1,
        ),
    )

    with pytest.raises(
        IdentifierFormatError,
        match="Config field sources\\[0\\] must not use Telegram invite links",
    ):
        load_app_config()


def test_load_app_config_rejects_invalid_filter_mode(
    set_service_env,
    semantic_valid_config_yaml: str,
) -> None:
    set_service_env(
        config_content=semantic_valid_config_yaml.replace("mode: any", "mode: some", 1),
    )

    with pytest.raises(
        ConfigSemanticError,
        match="Config field filters\\[0\\].mode must be one of: all, any",
    ):
        load_app_config()


def test_load_app_config_rejects_all_mode_event_type_mismatch(
    set_service_env,
    semantic_valid_config_yaml: str,
) -> None:
    set_service_env(
        config_content=semantic_valid_config_yaml.replace(
            '        event_type: drone\n',
            '        event_type: ballistic\n',
            1,
        ),
    )

    with pytest.raises(
        ConfigSemanticError,
        match="Config section filters\\[1\\] in all mode must use the same event_type and event_signal across include rules",
    ):
        load_app_config()


def test_load_app_config_rejects_all_mode_event_signal_mismatch(
    set_service_env,
    semantic_valid_config_yaml: str,
) -> None:
    set_service_env(
        config_content=semantic_valid_config_yaml.replace(
            '      - pattern: "shahed"\n'
            '        event_type: drone\n'
            '        event_signal: start\n',
            '      - pattern: "shahed"\n'
            '        event_type: drone\n'
            '        event_signal: clear\n',
            1,
        ),
    )

    with pytest.raises(
        ConfigSemanticError,
        match="Config section filters\\[1\\] in all mode must use the same event_type and event_signal across include rules",
    ):
        load_app_config()


def test_load_app_config_rejects_zero_publish_queue_size(
    set_service_env,
    semantic_valid_config_yaml: str,
) -> None:
    set_service_env(
        config_content=semantic_valid_config_yaml.replace(
            "  publish_queue_size: 200",
            "  publish_queue_size: 0",
        ),
    )

    with pytest.raises(
        ConfigSemanticError,
        match="Config field runtime.publish_queue_size must be greater than zero",
    ):
        load_app_config()
