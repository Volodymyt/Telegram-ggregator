# ADR 0003: Define DRY_RUN As No-Telegram Mode

## Status

Accepted

## Context

The project needs a supported operator mode for bootstrap verification, local environment checks, and future recovery-oriented runtime paths that should not contact Telegram at all.

`DRY_RUN` was initially ambiguous. Earlier planning language described it as a mode that suppresses publication side effects while still exercising the normal Telegram-backed pipeline. The implemented configuration and bootstrap path now follow a different rule:

- `DRY_RUN=1` must not perform Telegram network I/O,
- the application may still bootstrap non-Telegram components,
- the checked-in local profile may leave Telegram-facing values blank in this mode because Telegram transport is never initialized.

This decision affects multiple components and must remain discoverable so later storage, processing, publishing, and login work does not reintroduce Telegram calls behind the flag.

## Decision

`DRY_RUN` is defined as a no-Telegram runtime mode.

The runtime will:

- skip Telegram client initialization entirely when `DRY_RUN=1`,
- forbid Telegram network access from service bootstrap, login bootstrap, and future Telegram-facing components while the flag is enabled,
- continue allowing non-Telegram bootstrap and recovery-oriented runtime surfaces to start in this mode,
- allow `TG_API_ID`, `TG_API_HASH`, and `TARGET_CHANNEL` to be blank only in the `DRY_RUN=1` bootstrap profile,
- keep `python -m telegram_aggregator.login` disabled while `DRY_RUN=1`, because login is itself a Telegram operation,
- require Telegram-facing values again as soon as `DRY_RUN=0`.

The dry-run rule is enforced at the component boundary, not by forking the whole service into a separate global runtime shape. Telegram-facing components must handle the flag explicitly and avoid Telethon usage when it is enabled.

## Consequences

- Future reader, publisher, login, and other Telegram-facing components must treat `DRY_RUN` as a hard no-network constraint, not as a publish-only suppression flag.
- Tests for `DRY_RUN` should verify the absence of Telegram initialization or Telethon usage, not only the absence of publish side effects.
- End-to-end publication behavior must be validated in non-dry-run scenarios, because `DRY_RUN` no longer exercises the Telegram-backed path.
- The checked-in `.env.example` can remain a dry-run bootstrap profile with blank Telegram-facing values, but operator documentation must say so explicitly.
- Session-path resolution may still happen during config loading, but session creation, parent-directory handling, and authorization behavior remain separate decisions owned by the session-bootstrap work.
