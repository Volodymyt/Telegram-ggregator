"""Unit coverage for typed YAML file config loading."""

from __future__ import annotations

from pathlib import Path

import pytest

from telegram_aggregator.config import FileConfigError, load_file_config

_VALID_CONFIG_YAML = """\
sources:
  - "@channel1"
  - "@channel2"

filters:
  - mode: any
    include:
      - pattern: "Київ|Спуск|Балістика"
        event_type: ballistic
        event_signal: start
      - pattern: "чисто"
        event_type: ballistic
        event_signal: clear
    exclude:
      - "реклама|підписуйтесь"
    case_insensitive: true
    normalize: true
  - mode: all
    include:
      - pattern: "дрон"
        event_type: drone
        event_signal: start
      - pattern: "шахед"
        event_type: drone
        event_signal: start
    exclude: []
    case_insensitive: true
    normalize: true

repost:
  add_source_footer: true
  footer_template: "Source: {source}\\n{link}"
  fallback_on_copy_forbidden: "link_only"

runtime:
  processing_queue_size: 1000
  candidate_queue_size: 1000
  publish_queue_size: 200
  candidate_similarity_threshold: 0.82
  event_reopen_window_seconds: 300
  candidate_recovery_scan_seconds: 15
"""


def _write_config_file(tmp_path: Path, content: str = _VALID_CONFIG_YAML) -> Path:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(content, encoding="utf-8")
    return config_path


def test_load_file_config_parses_documented_shape(tmp_path: Path) -> None:
    config = load_file_config(_write_config_file(tmp_path))

    assert config.sources == ("@channel1", "@channel2")
    assert len(config.filters) == 2
    assert config.filters[0].mode == "any"
    assert config.filters[0].include[0].pattern == "Київ|Спуск|Балістика"
    assert config.filters[0].include[1].event_signal == "clear"
    assert config.filters[0].exclude == ("реклама|підписуйтесь",)
    assert config.filters[1].mode == "all"
    assert config.repost.footer_template == "Source: {source}\n{link}"
    assert config.runtime.candidate_similarity_threshold == pytest.approx(0.82)


def test_load_file_config_reports_yaml_syntax_with_location(tmp_path: Path) -> None:
    config_path = _write_config_file(
        tmp_path,
        "sources:\n  - '@channel1'\nfilters: [\n",
    )

    with pytest.raises(FileConfigError) as exc_info:
        load_file_config(config_path)

    message = str(exc_info.value)
    assert "Invalid YAML in config file:" in message
    assert "line " in message
    assert "column " in message


@pytest.mark.parametrize(
    "content",
    [
        _VALID_CONFIG_YAML
        + """\
runtime:
  processing_queue_size: 1000
  candidate_queue_size: 1000
  publish_queue_size: 200
  candidate_similarity_threshold: 0.82
  event_reopen_window_seconds: 300
  candidate_recovery_scan_seconds: 15
""",
        _VALID_CONFIG_YAML.replace("  - mode: any\n", "  - mode: any\n    mode: all\n", 1),
    ],
)
def test_load_file_config_rejects_duplicate_mapping_keys(
    tmp_path: Path,
    content: str,
) -> None:
    config_path = _write_config_file(tmp_path, content)

    with pytest.raises(FileConfigError) as exc_info:
        load_file_config(config_path)

    message = str(exc_info.value)
    assert "Invalid YAML in config file:" in message
    assert "found duplicate key" in message


def test_load_file_config_rejects_unhashable_mapping_key(tmp_path: Path) -> None:
    config_path = _write_config_file(
        tmp_path,
        """\
sources:
  - "@channel1"
  - "@channel2"

filters:
  - ? [1, 2]
    : value

repost:
  add_source_footer: true
  footer_template: "Source: {source}\\n{link}"
  fallback_on_copy_forbidden: "link_only"

runtime:
  processing_queue_size: 1000
  candidate_queue_size: 1000
  publish_queue_size: 200
  candidate_similarity_threshold: 0.82
  event_reopen_window_seconds: 300
  candidate_recovery_scan_seconds: 15
""",
    )

    with pytest.raises(FileConfigError) as exc_info:
        load_file_config(config_path)

    message = str(exc_info.value)
    assert "Invalid YAML in config file:" in message
    assert "found unhashable key" in message


def test_load_file_config_rejects_non_mapping_root(tmp_path: Path) -> None:
    config_path = _write_config_file(tmp_path, "- just\n- a\n- list\n")

    with pytest.raises(FileConfigError, match="Config section document root must be a mapping"):
        load_file_config(config_path)


def test_load_file_config_rejects_empty_filter_groups_list(tmp_path: Path) -> None:
    config_path = _write_config_file(
        tmp_path,
        """\
sources: []
filters: []

repost:
  add_source_footer: true
  footer_template: "Source: {source}\\n{link}"
  fallback_on_copy_forbidden: "link_only"

runtime:
  processing_queue_size: 1000
  candidate_queue_size: 1000
  publish_queue_size: 200
  candidate_similarity_threshold: 0.82
  event_reopen_window_seconds: 300
  candidate_recovery_scan_seconds: 15
""",
    )

    with pytest.raises(
        FileConfigError,
        match="Config field filters must contain at least one item",
    ):
        load_file_config(config_path)


@pytest.mark.parametrize(
    ("content", "message"),
    [
        (
            """\
sources: []
filters:
  - mode: any
    include: []
    exclude: []
    case_insensitive: true
    normalize: true
repost:
  add_source_footer: true
  footer_template: "Source: {source}\\n{link}"
  fallback_on_copy_forbidden: "link_only"
""",
            "missing keys: runtime",
        ),
        (
            _VALID_CONFIG_YAML
            + "\ntelegram:\n  api_id: 123\n",
            "unexpected keys: telegram",
        ),
    ],
)
def test_load_file_config_rejects_invalid_top_level_keys(
    tmp_path: Path,
    content: str,
    message: str,
) -> None:
    config_path = _write_config_file(tmp_path, content)

    with pytest.raises(FileConfigError, match=message):
        load_file_config(config_path)


def test_load_file_config_rejects_invalid_include_rule_shape(tmp_path: Path) -> None:
    config_path = _write_config_file(
        tmp_path,
        _VALID_CONFIG_YAML.replace(
            '        event_signal: start\n',
            '        severity: high\n',
            1,
        ),
    )

    with pytest.raises(
        FileConfigError,
        match="Config section filters\\[0\\].include\\[0\\] has invalid keys",
    ):
        load_file_config(config_path)


def test_load_file_config_rejects_invalid_event_signal(tmp_path: Path) -> None:
    config_path = _write_config_file(
        tmp_path,
        _VALID_CONFIG_YAML.replace("event_signal: clear", "event_signal: stop"),
    )

    with pytest.raises(
        FileConfigError,
        match="Config field filters\\[0\\].include\\[1\\].event_signal must be one of:",
    ):
        load_file_config(config_path)


@pytest.mark.parametrize(
    ("content", "message"),
    [
        (
            _VALID_CONFIG_YAML.replace('  - "@channel2"\n', "  - 42\n", 1),
            "Config field sources\\[1\\] must be a string",
        ),
        (
            _VALID_CONFIG_YAML.replace('      - "реклама|підписуйтесь"\n', "      - 42\n", 1),
            "Config field filters\\[0\\].exclude\\[0\\] must be a string",
        ),
    ],
)
def test_load_file_config_rejects_non_string_list_items(
    tmp_path: Path,
    content: str,
    message: str,
) -> None:
    config_path = _write_config_file(tmp_path, content)

    with pytest.raises(FileConfigError, match=message):
        load_file_config(config_path)


@pytest.mark.parametrize(
    ("content", "message"),
    [
        (
            _VALID_CONFIG_YAML.replace(
                "    case_insensitive: true",
                '    case_insensitive: "yes"',
                1,
            ),
            "Config field filters\\[0\\].case_insensitive must be a boolean",
        ),
        (
            _VALID_CONFIG_YAML.replace(
                "    normalize: true",
                '    normalize: "yes"',
                1,
            ),
            "Config field filters\\[0\\].normalize must be a boolean",
        ),
    ],
)
def test_load_file_config_rejects_non_boolean_filter_toggles(
    tmp_path: Path,
    content: str,
    message: str,
) -> None:
    config_path = _write_config_file(tmp_path, content)

    with pytest.raises(FileConfigError, match=message):
        load_file_config(config_path)


def test_load_file_config_rejects_boolean_runtime_integer(tmp_path: Path) -> None:
    config_path = _write_config_file(
        tmp_path,
        _VALID_CONFIG_YAML.replace("  publish_queue_size: 200", "  publish_queue_size: true"),
    )

    with pytest.raises(
        FileConfigError,
        match="Config field runtime.publish_queue_size must be an integer",
    ):
        load_file_config(config_path)


def test_load_file_config_converts_integer_threshold_to_float(tmp_path: Path) -> None:
    config_path = _write_config_file(
        tmp_path,
        _VALID_CONFIG_YAML.replace(
            "  candidate_similarity_threshold: 0.82",
            "  candidate_similarity_threshold: 1",
        ),
    )

    config = load_file_config(config_path)

    assert config.runtime.candidate_similarity_threshold == 1.0
