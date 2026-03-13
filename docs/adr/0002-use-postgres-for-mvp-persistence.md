# ADR 0002: Use Postgres For MVP Message And Event Persistence

## Status

Accepted

## Context

The service must persist source messages, candidate state, logical event state, and processing status across restarts.

The MVP also needs a simple way to:

- prevent duplicate reposts with a durable unique key,
- track where each source message is in the pipeline,
- track which logical event a candidate belongs to,
- close and reopen logical events across restarts,
- store publish outcomes and errors,
- inspect state during operations and debugging.

In-memory queues are sufficient for runtime coordination, but they are not durable stores. The persistence layer therefore needs to be the canonical source of truth for both message state and logical event state.

## Decision

The MVP will use Postgres as the canonical persistence layer for source messages, candidate state, and logical event state.

The runtime will:

- store source messages and their processing status in Postgres,
- store logical events and their lifecycle state in Postgres,
- use a unique key on `(source_chat_id, source_message_id)` for durable source-message deduplication,
- let the candidate aggregator recover durable `candidate` rows from Postgres after restart,
- keep processing, candidate, and publish queues in-process instead of introducing an external broker,
- continue storing the Telegram session as a mounted file outside the container image.

## Consequences

- The runtime requires a Postgres connection string such as `DATABASE_URL`.
- Documentation must treat Postgres, not SQLite, as the canonical MVP storage solution.
- Operators gain a queryable store for message status, event lifecycle state, publish outcomes, and failures.
- Queue state remains ephemeral, so workers and the candidate aggregator must derive recoverable state from Postgres on startup when needed.
- Redis or another broker is not required for the MVP.
