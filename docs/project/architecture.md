# Architecture

This document is the short architectural overview. The implementation-oriented component design lives in [`architecture-spec.md`](architecture-spec.md).

## Target System Design

The target MVP is a single asynchronous Python service that:

- connects to Telegram through a persisted user session,
- uses Telethon to subscribe to source message events,
- stores source messages, candidate state, and logical event state in Postgres,
- filters messages into typed publication candidates,
- aggregates candidates into logical events with event-level deduplication,
- publishes only selected event candidates to one target channel through a separate internal publish flow.

## Core Components

- Message reader: registers Telethon new-message handlers, normalizes incoming events, and records newly seen messages.
- Message store: keeps source messages, candidate state, and logical event state in Postgres.
- Processing flow: uses an in-process queue and worker to apply typed include and exclude rules and mark publication candidates.
- Candidate aggregation flow: deduplicates candidates across sources, tracks logical event lifecycle, and selects the canonical source for publication.
- Publish flow: uses a separate in-process queue and worker to serialize target-channel publication and retries.
- Observability: emits structured logs and exposes health status.

## Telegram Constraints

- Telegram Bot API is not sufficient for reading arbitrary external source channels unless the bot is explicitly added with the required permissions.
- The service therefore reads source messages through a Telegram user account session over MTProto.
- Telethon owns transport, reconnects, and event subscription. The application only implements message handling and processing logic.

## Deployment Model

- One deployable Python service in Docker.
- Mounted Telegram session file for user authorization state.
- Postgres as the canonical persistence layer for message, candidate, and event state.
- File-based configuration plus environment variables for secrets and runtime parameters.

## Current Repository Note

- The current repository still contains a minimal placeholder scaffold.
- `src/Telegram-aggregator/` should be treated as a legacy scaffold, not the target implementation layout.
- The canonical package root for new implementation work is `src/telegram_aggregator/`.
