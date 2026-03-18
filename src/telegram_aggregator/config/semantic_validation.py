"""Startup semantic validation for the canonical config boundary."""

from __future__ import annotations

import math
import re
from typing import TYPE_CHECKING

from telethon.utils import parse_username

from telegram_aggregator.config.app_config import AppConfigError

if TYPE_CHECKING:
    from telegram_aggregator.config.app_config import AppConfig
    from telegram_aggregator.config.file_config import FilterGroupConfig, RuntimeConfig

_VALID_FILTER_MODES = frozenset({"any", "all"})
_NUMERIC_IDENTIFIER_RE = re.compile(r"^-?\d+$")
_URL_PREFIX_RE = re.compile(
    r"^(?:https?://)?(?:www\.)?(?:telegram\.(?:me|dog)|t\.me)/",
    re.IGNORECASE,
)


class ConfigSemanticError(AppConfigError):
    """Raised when config values are well-typed but semantically invalid."""


class IdentifierFormatError(ConfigSemanticError):
    """Raised when a Telegram source or target identifier uses an unsupported form."""


def validate_app_config(config: AppConfig) -> None:
    """Validate startup semantics after the canonical AppConfig is assembled."""
    # `load_file_config()` already owns YAML shape/type validation, including the
    # boolean startup toggles (`case_insensitive` and `normalize`). This pass
    # handles post-assembly identifier and cross-field semantics.

    _validate_sources(config.file_config.sources)
    _validate_filter_groups(config.file_config.filters)
    _validate_runtime_queue_sizes(config.file_config.runtime)

    if not (config.dry_run and config.target_channel == ""):
        _validate_target_identifier(
            config.target_channel,
            "Environment variable TARGET_CHANNEL",
        )


def _validate_sources(sources: tuple[str, ...]) -> None:
    for index, source in enumerate(sources):
        _validate_source_identifier(source, f"Config field sources[{index}]")


def _validate_source_identifier(value: str, context: str) -> None:
    if value != value.strip():
        raise IdentifierFormatError(
            f"{context} must not contain leading or trailing whitespace"
        )

    if _is_numeric_identifier(value):
        return

    if value.startswith("@"):
        username, is_invite = parse_username(value)
        if username is not None and not is_invite:
            return

    if _looks_like_telegram_url(value):
        username, is_invite = parse_username(value)
        if is_invite:
            raise IdentifierFormatError(
                f"{context} must not use Telegram invite links; use @username, "
                "t.me/<username>, or a non-zero numeric id"
            )

        if username is not None:
            return

    raise IdentifierFormatError(
        f"{context} must be a Telegram source identifier in one of these forms: "
        "@username, t.me/<username>, or non-zero numeric id"
    )


def _validate_target_identifier(value: str, context: str) -> None:
    if _is_numeric_identifier(value):
        return

    if _looks_like_telegram_url(value):
        raise IdentifierFormatError(
            f"{context} must use username, @username, or numeric id, not a Telegram URL"
        )

    username, is_invite = parse_username(value)
    if username is None or is_invite:
        raise IdentifierFormatError(
            f"{context} must be a Telegram target identifier in one of these forms: "
            "username, @username, or non-zero numeric id"
        )


def _validate_filter_groups(filters: tuple[FilterGroupConfig, ...]) -> None:
    for index, filter_group in enumerate(filters):
        context = f"filters[{index}]"

        if filter_group.mode not in _VALID_FILTER_MODES:
            allowed_modes = ", ".join(sorted(_VALID_FILTER_MODES))
            raise ConfigSemanticError(
                f"Config field {context}.mode must be one of: {allowed_modes}"
            )

        if filter_group.mode != "all" or len(filter_group.include) < 2:
            continue

        event_type = filter_group.include[0].event_type
        event_signal = filter_group.include[0].event_signal

        for rule in filter_group.include[1:]:
            if rule.event_type != event_type or rule.event_signal != event_signal:
                raise ConfigSemanticError(
                    f"Config section {context} in all mode must use the same "
                    "event_type and event_signal across include rules"
                )


def _validate_runtime_queue_sizes(runtime: RuntimeConfig) -> None:
    _require_positive_int(
        runtime.processing_queue_size,
        "Config field runtime.processing_queue_size",
    )
    _require_positive_int(
        runtime.candidate_queue_size,
        "Config field runtime.candidate_queue_size",
    )
    _require_positive_int(
        runtime.publish_queue_size,
        "Config field runtime.publish_queue_size",
    )
    _require_unit_float(
        runtime.candidate_similarity_threshold,
        "Config field runtime.candidate_similarity_threshold",
    )
    _require_positive_int(
        runtime.event_reopen_window_seconds,
        "Config field runtime.event_reopen_window_seconds",
    )
    _require_positive_int(
        runtime.candidate_recovery_scan_seconds,
        "Config field runtime.candidate_recovery_scan_seconds",
    )


def _require_positive_int(value: int, context: str) -> None:
    if value <= 0:
        raise ConfigSemanticError(f"{context} must be greater than zero")


def _require_unit_float(value: float, context: str) -> None:
    if math.isnan(value) or math.isinf(value) or value < 0.0 or value > 1.0:
        raise ConfigSemanticError(f"{context} must be between 0.0 and 1.0")


def _is_numeric_identifier(value: str) -> bool:
    if _NUMERIC_IDENTIFIER_RE.fullmatch(value) is None:
        return False

    return int(value) != 0


def _looks_like_telegram_url(value: str) -> bool:
    return _URL_PREFIX_RE.match(value) is not None
