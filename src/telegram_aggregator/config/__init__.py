"""Configuration package placeholder."""

from telegram_aggregator.config.runtime import (
    LoggingConfig,
    RuntimeConfig,
    RuntimeConfigError,
    TGConfig,
    load_runtime_config,
)

__all__ = [
    "LoggingConfig",
    "RuntimeConfig",
    "RuntimeConfigError",
    "TGConfig",
    "load_runtime_config",
]
