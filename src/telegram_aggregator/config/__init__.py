"""Configuration package placeholder."""

from telegram_aggregator.config.runtime import (
    LoggingConfig,
    RuntimeConfig,
    TGConfig,
    load_runtime_config,
)

__all__ = [
    "LoggingConfig",
    "RuntimeConfig",
    "TGConfig",
    "load_runtime_config",
]
