"""Typed YAML file configuration models and loader."""

from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from telegram_aggregator.config.app_config import AppConfigError

_ROOT_KEYS = frozenset({"sources", "filters", "repost", "runtime"})
_FILTER_KEYS = frozenset(
    {"mode", "include", "exclude", "case_insensitive", "normalize"}
)
_INCLUDE_RULE_KEYS = frozenset({"pattern", "event_type", "event_signal"})
_REPOST_KEYS = frozenset(
    {"add_source_footer", "footer_template", "fallback_on_copy_forbidden"}
)
_RUNTIME_KEYS = frozenset(
    {
        "processing_queue_size",
        "candidate_queue_size",
        "publish_queue_size",
        "candidate_similarity_threshold",
        "event_reopen_window_seconds",
        "candidate_recovery_scan_seconds",
    }
)
_VALID_EVENT_SIGNALS = frozenset({"start", "clear"})


@dataclass(frozen=True)
class IncludeRuleConfig:
    pattern: str
    event_type: str
    event_signal: str


@dataclass(frozen=True)
class FilterGroupConfig:
    mode: str
    include: tuple[IncludeRuleConfig, ...]
    exclude: tuple[str, ...]
    case_insensitive: bool
    normalize: bool


@dataclass(frozen=True)
class RepostConfig:
    add_source_footer: bool
    footer_template: str
    fallback_on_copy_forbidden: str


@dataclass(frozen=True)
class RuntimeConfig:
    processing_queue_size: int
    candidate_queue_size: int
    publish_queue_size: int
    candidate_similarity_threshold: float
    event_reopen_window_seconds: int
    candidate_recovery_scan_seconds: int


@dataclass(frozen=True)
class FileConfig:
    sources: tuple[str, ...]
    filters: tuple[FilterGroupConfig, ...]
    repost: RepostConfig
    runtime: RuntimeConfig


class FileConfigError(AppConfigError):
    """Raised when the YAML config file is malformed or has an invalid shape."""


class _UniqueKeySafeLoader(yaml.SafeLoader):
    """SafeLoader variant that rejects duplicate mapping keys."""


def load_file_config(path: Path) -> FileConfig:
    """Load and validate the typed YAML config contract from disk."""

    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = yaml.load(handle, Loader=_UniqueKeySafeLoader)
    except OSError as exc:
        raise FileConfigError(f"Could not read config file: {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise FileConfigError(_format_yaml_parse_error(path, exc)) from exc

    root = _require_mapping(payload, "document root")
    _require_exact_keys(root, _ROOT_KEYS, "document root")

    return FileConfig(
        sources=_require_string_list(root["sources"], "sources"),
        filters=_parse_filter_groups(root["filters"]),
        repost=_parse_repost_config(root["repost"]),
        runtime=_parse_runtime_config(root["runtime"]),
    )


def _construct_mapping_with_unique_keys(
    loader: _UniqueKeySafeLoader,
    node: yaml.nodes.MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    mapping: dict[Any, Any] = {}

    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)

        if not isinstance(key, Hashable):
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "found unhashable key",
                key_node.start_mark,
            )

        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key ({key!r})",
                key_node.start_mark,
            )

        mapping[key] = loader.construct_object(value_node, deep=deep)

    return mapping


_UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_mapping_with_unique_keys,
)


def _parse_filter_groups(payload: Any) -> tuple[FilterGroupConfig, ...]:
    groups = _require_non_empty_list(payload, "filters")

    return tuple(_parse_filter_group(group, index) for index, group in enumerate(groups))


def _parse_filter_group(payload: Any, index: int) -> FilterGroupConfig:
    section_name = f"filters[{index}]"
    section = _require_mapping(payload, section_name)
    _require_exact_keys(section, _FILTER_KEYS, section_name)
    include_values = _require_list(section["include"], f"{section_name}.include")
    include_rules = tuple(
        _parse_include_rule(rule, group_index=index, rule_index=rule_index)
        for rule_index, rule in enumerate(include_values)
    )

    return FilterGroupConfig(
        mode=_require_string(section["mode"], f"{section_name}.mode"),
        include=include_rules,
        exclude=_require_string_list(section["exclude"], f"{section_name}.exclude"),
        case_insensitive=_require_bool(
            section["case_insensitive"],
            f"{section_name}.case_insensitive",
        ),
        normalize=_require_bool(section["normalize"], f"{section_name}.normalize"),
    )


def _parse_include_rule(
    payload: Any,
    *,
    group_index: int,
    rule_index: int,
) -> IncludeRuleConfig:
    section_name = f"filters[{group_index}].include[{rule_index}]"
    section = _require_mapping(payload, section_name)
    _require_exact_keys(section, _INCLUDE_RULE_KEYS, section_name)
    event_signal = _require_string(section["event_signal"], f"{section_name}.event_signal")

    if event_signal not in _VALID_EVENT_SIGNALS:
        allowed = ", ".join(sorted(_VALID_EVENT_SIGNALS))
        raise FileConfigError(
            f"Config field {section_name}.event_signal must be one of: {allowed}"
        )

    return IncludeRuleConfig(
        pattern=_require_string(section["pattern"], f"{section_name}.pattern"),
        event_type=_require_string(section["event_type"], f"{section_name}.event_type"),
        event_signal=event_signal,
    )


def _parse_repost_config(payload: Any) -> RepostConfig:
    section_name = "repost"
    section = _require_mapping(payload, section_name)
    _require_exact_keys(section, _REPOST_KEYS, section_name)

    return RepostConfig(
        add_source_footer=_require_bool(
            section["add_source_footer"],
            "repost.add_source_footer",
        ),
        footer_template=_require_string(
            section["footer_template"],
            "repost.footer_template",
        ),
        fallback_on_copy_forbidden=_require_string(
            section["fallback_on_copy_forbidden"],
            "repost.fallback_on_copy_forbidden",
        ),
    )


def _parse_runtime_config(payload: Any) -> RuntimeConfig:
    section_name = "runtime"
    section = _require_mapping(payload, section_name)
    _require_exact_keys(section, _RUNTIME_KEYS, section_name)

    return RuntimeConfig(
        processing_queue_size=_require_int(
            section["processing_queue_size"],
            "runtime.processing_queue_size",
        ),
        candidate_queue_size=_require_int(
            section["candidate_queue_size"],
            "runtime.candidate_queue_size",
        ),
        publish_queue_size=_require_int(
            section["publish_queue_size"],
            "runtime.publish_queue_size",
        ),
        candidate_similarity_threshold=_require_float(
            section["candidate_similarity_threshold"],
            "runtime.candidate_similarity_threshold",
        ),
        event_reopen_window_seconds=_require_int(
            section["event_reopen_window_seconds"],
            "runtime.event_reopen_window_seconds",
        ),
        candidate_recovery_scan_seconds=_require_int(
            section["candidate_recovery_scan_seconds"],
            "runtime.candidate_recovery_scan_seconds",
        ),
    )


def _require_mapping(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FileConfigError(f"Config section {context} must be a mapping")

    return value


def _require_exact_keys(
    mapping: dict[str, Any],
    expected_keys: frozenset[str],
    context: str,
) -> None:
    if any(not isinstance(key, str) for key in mapping):
        raise FileConfigError(f"Config section {context} must use string keys only")

    actual_keys = frozenset(mapping)
    missing_keys = sorted(expected_keys - actual_keys)
    unexpected_keys = sorted(actual_keys - expected_keys)

    if not missing_keys and not unexpected_keys:
        return

    problems: list[str] = []

    if missing_keys:
        problems.append(f"missing keys: {', '.join(missing_keys)}")

    if unexpected_keys:
        problems.append(f"unexpected keys: {', '.join(unexpected_keys)}")

    raise FileConfigError(
        f"Config section {context} has invalid keys ({'; '.join(problems)})"
    )


def _require_list(value: Any, context: str) -> list[Any]:
    if not isinstance(value, list):
        raise FileConfigError(f"Config field {context} must be a list")

    return value


def _require_non_empty_list(value: Any, context: str) -> list[Any]:
    items = _require_list(value, context)

    if not items:
        raise FileConfigError(f"Config field {context} must contain at least one item")

    return items


def _require_string_list(value: Any, context: str) -> tuple[str, ...]:
    items = _require_list(value, context)

    return tuple(
        _require_string(item, f"{context}[{index}]")
        for index, item in enumerate(items)
    )


def _require_string(value: Any, context: str) -> str:
    if not isinstance(value, str):
        raise FileConfigError(f"Config field {context} must be a string")

    return value


def _require_bool(value: Any, context: str) -> bool:
    if not isinstance(value, bool):
        raise FileConfigError(f"Config field {context} must be a boolean")

    return value


def _require_int(value: Any, context: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise FileConfigError(f"Config field {context} must be an integer")

    return value


def _require_float(value: Any, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise FileConfigError(f"Config field {context} must be a number")

    return float(value)


def _format_yaml_parse_error(path: Path, exc: yaml.YAMLError) -> str:
    message = f"Invalid YAML in config file: {path}"
    mark = getattr(exc, "problem_mark", None)
    problem = getattr(exc, "problem", None)

    if mark is not None:
        message += f" at line {mark.line + 1}, column {mark.column + 1}"

    if problem:
        message += f": {problem}"
    else:
        message += f": {exc}"

    return message
