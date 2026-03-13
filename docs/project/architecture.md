# Architecture

## Target System Design

The target MVP is a long-running Python service that listens to Telegram source channels through an authenticated user session, filters incoming messages, and republishes matches to a target channel.

## Core Components

### Telegram Listener

- Connects to Telegram through MTProto using a persisted user session.
- Subscribes to new message events for configured sources.
- Delivers source message events into internal processing flow.

### Filter Engine

- Compiles include and exclude patterns.
- Applies `any` or `all` matching mode.
- Evaluates message text and media captions.
- Applies optional normalization before matching.

### Dedup Store

- Persists posted message identifiers in SQLite.
- Tracks at least source identifier, source message identifier, post timestamp, and target message identifier.
- Preserves repost state across service restarts.

### Publish Worker

- Uses an internal queue to serialize publication work.
- Applies throttling to reduce rate-limit pressure.
- Handles flood waits and retry backoff behavior.
- Publishes text, media, attribution, and fallback output according to configuration.

### Observability

- Emits structured logs.
- Exposes a health signal through a container health check and may optionally expose an HTTP health endpoint.

## Telegram Constraints

- Telegram Bot API is not sufficient for reading arbitrary external source channels unless the bot is explicitly added with the required permissions.
- The target design therefore reads source messages through a Telegram user account session.
- This design requires `api_id`, `api_hash`, and one-time authorization of the account session.

## Recommended Technology Choices

- Telethon as the asynchronous MTProto client.
- SQLite as the default persistent deduplication store.
- Python `asyncio` and an in-memory queue for publication flow control.
- Structured logging through either the standard logging module or `structlog`.

## Deployment Model

- Base image target: `python:3.12-slim`, with `3.11` also acceptable when required.
- State volume target: `/data` for the Telegram session file and SQLite database.
- File-based configuration mounted into the container, with environment variables for runtime secrets and parameters.
- Compose-based local deployment support through mounted data and configuration files.

## Current Repository Note

- The current repository still contains a minimal placeholder application scaffold.
- The specification currently refers to a target runtime shape such as `python -m app` and optional `python -m app.login`.
- The current `Dockerfile` entrypoint differs from that target shape, so documentation must treat the target runtime contract and current repository scaffold as separate concerns until implementation aligns them.
