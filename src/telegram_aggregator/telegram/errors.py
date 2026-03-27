"""Telegram-specific error types."""


class SessionBootstrapError(ValueError):
    """Raised when Telegram session bootstrap cannot continue."""


class SessionPathError(SessionBootstrapError):
    """Raised when the configured Telegram session path cannot be used."""


class SessionAuthorizationError(SessionBootstrapError):
    """Raised when Telegram session authorization is missing or fails."""
