# ADR 0001: Use MTProto User Session For Source Reading

## Status

Accepted

## Context

The service must read messages from a configurable list of Telegram source channels and chats.

Telegram Bot API is not sufficient for this requirement when the source channels are external and the bot is not explicitly added with the required permissions. A bot cannot behave like an RSS reader that subscribes to arbitrary Telegram channels.

The MVP therefore needs a Telegram client approach that can read channels available to an authenticated user account.

## Decision

The service will use Telethon with a persisted Telegram user session to read source messages through MTProto.

## Consequences

- The runtime requires `TG_API_ID` and `TG_API_HASH`.
- A one-time account authorization step is required before normal daemon operation.
- The session file must be stored outside the image, typically in a mounted data volume.
- Secrets must be injected through environment variables rather than baked into the container image.
- Operational documentation must cover first-time login and session persistence.
