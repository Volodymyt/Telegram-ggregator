"""Canonical login bootstrap placeholder."""

from telegram_aggregator.config import AppConfigError, load_app_config


def run_login() -> None:
    """Route login startup through the canonical bootstrap boundary."""

    try:
        config = load_app_config()
    except AppConfigError as exc:
        raise SystemExit(str(exc)) from None

    if config.dry_run:
        raise SystemExit(
            "Login bootstrap is disabled when DRY_RUN is enabled because "
            "Telegram I/O is not allowed in dry-run mode."
        )

    raise SystemExit(
        "Login bootstrap is not implemented yet. "
        f"Resolved session path: {config.telegram.session_path}. "
        "Use the canonical telegram_aggregator.bootstrap.run_login entrypoint for "
        "future session wiring."
    )
