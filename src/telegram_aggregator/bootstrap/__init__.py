"""Bootstrap entrypoints for service and login flows."""


def run_service() -> None:
    """Run the canonical service bootstrap flow."""

    from telegram_aggregator.bootstrap.service import run_service as _run_service

    _run_service()


def run_login() -> None:
    """Run the canonical login bootstrap flow."""

    from telegram_aggregator.bootstrap.login import run_login as _run_login

    _run_login()


__all__ = ["run_login", "run_service"]
