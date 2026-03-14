# MVP Delivery Plan

Status: Draft
Owner: TBD
Last updated: 2026-03-14

## Goal

Turn the approved MVP architecture into a delivery-ready investigation document that can later be decomposed into concrete backlog items without reopening core implementation decisions.

## Summary

The architecture is already stable enough to drive execution:

- one deployable asynchronous Python service;
- component-oriented modular monolith;
- Telethon for Telegram transport, reconnects, and subscriptions;
- Postgres as the canonical persistence layer;
- in-process `asyncio.Queue` for processing, candidate aggregation, and publishing.

The current repository is not implementation-ready yet. It still runs a legacy placeholder entrypoint, lacks the canonical package structure, has no storage layer, no config layer, no test harness, and no execution bridge between architecture docs and backlog planning.

Delivery should therefore start with one foundational milestone, then move through vertical end-to-end slices, and finish with MVP hardening.

This document must also stay specific enough to support backlog decomposition without reopening core technical decisions during normal execution.

## Fixed Delivery Constraints

The following constraints are already fixed by the architecture and requirements and must not be revisited during normal task decomposition:

- The canonical package root is `src/telegram_aggregator/`.
- The service remains a single deployable Python process for the MVP.
- Telethon owns MTProto transport and reconnect behavior.
- Postgres is the only canonical durable state store.
- Processing, candidate, and publish queues remain in-process runtime coordination primitives.
- `first arrival wins` is the canonical source-selection rule.
- Candidate deduplication operates within the same `target_channel` and `event_type`.
- Candidate similarity uses `difflib.SequenceMatcher` with a threshold of `0.82`.
- A repeated matching `start` signal more than 5 minutes after the original event start opens a new event.
- A `clear` signal closes only an active event of the same `event_type` and is never published.
- `DRY_RUN` remains a supported operator mode and must suppress Telegram side effects without bypassing intake, filtering, aggregation, or persistence logic.
- Restart recovery must cover durable work that can be left behind in `candidate`, `selected_for_publish`, or `publishing` state.

## Investigation Findings

### Repo Gaps

- `src/Telegram-aggregator/__main__.py` is still a placeholder loop.
- `Dockerfile` still starts the legacy package instead of `src/telegram_aggregator/`.
- `src/telegram_aggregator/` does not yet contain the target runtime modules.
- `requirements.txt` is still a placeholder and does not define a reproducible runtime baseline.
- There is no schema, migration flow, repository layer, or event persistence implementation.
- There is no validated config/settings layer for the documented environment and YAML contract.
- There is no worker/runtime bootstrap, login flow, health endpoint, or structured observability.
- There is no test harness for filters, deduplication, lifecycle handling, or restart recovery.

### Delivery Implication

The repo is at a pre-MVP foundation stage. It is not ready to start with business features directly. The first milestone must establish the executable runtime baseline before feature slices begin.

## Locked Technical Defaults

These defaults are chosen now to remove ambiguity before backlog decomposition.

### Runtime and Package Layout

- Build new implementation only under `src/telegram_aggregator/`.
- Use one top-level service runtime plus a dedicated login entrypoint.
- Organize code by runtime component:
  - `bootstrap/`
  - `config/`
  - `storage/`
  - `reading/`
  - `processing/`
  - `candidate_aggregation/`
  - `publishing/`
  - `observability/`

### Storage

- Use PostgreSQL with SQLAlchemy 2.x async engine and SQLAlchemy Core, not ORM models.
- Use Alembic for schema migrations.
- Keep persistence centered on `message_records` and `event_records`.
- Use transactional row claiming with `SELECT ... FOR UPDATE SKIP LOCKED` for candidate recovery and processing where row ownership matters.

### Normalization

- Use a shared normalization pipeline for filter matching:
  - Unicode normalization with NFKC;
  - lowercasing;
  - trimming;
  - collapsing repeated whitespace;
  - replacing `ё` with `е`.
- Build `candidate_signature` from normalized text after stripping URLs, usernames, punctuation, and repeated whitespace.
- Match against message text and media captions only.

### Publishing

- The publish worker is the only component allowed to publish to the target channel.
- Default publish behavior:
  - text posts are sent as text with attribution footer;
  - photo posts with captions are copied when possible;
  - if copying is forbidden, fallback is `link_only` text output with source attribution instead of media re-upload in the MVP.
- Album handling remains reduced to a first-message strategy in the MVP.

### Publish Retry and Recovery

- `FloodWaitError` is handled by sleeping for the exact reported duration and retrying the same publication job.
- Other transient publish failures use persisted retry state with exponential backoff of `5s`, `15s`, `30s`, `60s`, then capped `300s` retries for the MVP.
- Non-retriable publish failures mark the selected message as `publish_failed` and the owning event as `failed` without further retries.
- Bootstrap must rebuild publication jobs from Postgres for rows left in `selected_for_publish` or `publishing` before steady-state processing is considered healthy.

### Operator Experience and Observability

- The primary login flow is `python -m telegram_aggregator.login`.
- `LOGIN=1` remains a compatibility path for containerized bootstrap.
- Observability defaults to structured JSON logs plus a lightweight HTTP health endpoint.
- The health endpoint should expose readiness at a high level for Telegram, Postgres, and worker liveness.
- Config validation must support source identifiers given as `@username`, `t.me/...`, or numeric ids where supported, and target identifiers as username or numeric id.
- `DRY_RUN` must exercise the normal pipeline up to publication decision while suppressing target-channel writes.

### Delivery Guardrails

- Task decomposition must keep traceability to the documented YAML and environment contract, including `LOG_LEVEL`, `DRY_RUN`, queue sizes, normalization toggles, and login flows.
- Capacity and operability tasks must not drop the MVP targets of at least 100 configured sources, 10 to 30 seconds normal end-to-end latency, and a small VPS deployment profile of `1 vCPU / 512 MB` or better.
- Operational hardening tasks must keep secrets out of the image and preserve compatibility with reduced-privilege containers and, where practical for the MVP, a read-only root filesystem.

### Milestone Staging

- The first end-to-end publish slice may be text-only.
- Photo-with-caption support is required by the final MVP hardening milestone, not by the first vertical slice.

## Internal Contracts To Preserve

Future implementation and task decomposition should preserve these internal types and contracts:

- `CandidateMessage`
- `EventSignal`
- `EventRecord`
- `PublicationJob`
- `message_records` statuses:
  - `received`
  - `filtered_out`
  - `candidate`
  - `suppressed_duplicate`
  - `selected_for_publish`
  - `publishing`
  - `published`
  - `publish_failed`
  - `clear_processed`
  - `orphan_clear`
- `event_records.state`:
  - `open`
  - `closed`
- `event_records.publish_status`:
  - `pending`
  - `published`
  - `failed`

## Requirement Coverage Guardrails

These items must remain visible during task decomposition even when they do not dominate milestone naming:

- M0 must cover config/runtime validation for source and target identifier formats, `LOG_LEVEL`, `DRY_RUN`, queue sizes, YAML toggles, and both login entry paths.
- M1 must preserve `case_insensitive` and normalization-driven filter behavior from the configuration contract, not only the regex matching core.
- M2 must keep `DRY_RUN` and attribution behavior testable in the first end-to-end publish slice.
- M3 must cover restart recovery for `candidate`, `selected_for_publish`, and `publishing` states, not only candidate aggregation recovery.
- M4 must include explicit verification for capacity, latency, runtime security posture, and final operator run instructions.

## Workstreams

### 1. Foundation

- Canonical package/runtime realignment.
- Dependency and tooling baseline.
- Config/settings parsing and validation.
- Service bootstrap and worker lifecycle.
- Minimal observability and health.
- Test harness foundation.

### 2. Storage

- Schema and migration setup.
- Connection management.
- Repositories for message and event state.
- Idempotent inserts and state transitions.
- Candidate claiming and restart-safe ownership rules.

### 3. Intake and Processing

- Telethon session startup.
- Source subscription and message reading.
- Internal message normalization.
- Include/exclude filter engine.
- Processing queue and candidate classification.

### 4. Candidate Aggregation and Event Lifecycle

- Candidate queue consumer.
- Recovery scan for persisted `candidate` rows.
- Candidate signature generation.
- Fuzzy matching against open events.
- Duplicate suppression and event linking.
- `clear` handling and event closure.

### 5. Publishing and Resilience

- Publish queue and serialized publish worker.
- Payload formatting and attribution footer.
- Telethon target-channel publish adapter.
- Flood wait handling.
- Restart-safe recovery of `selected_for_publish` and `publishing` rows.
- Terminal failure handling and persisted retry state.
- Copy-forbidden fallback behavior.

### 6. Operability and Acceptance

- Docker/runtime alignment.
- Environment and run instructions.
- `DRY_RUN` verification.
- Health and readiness verification.
- Capacity and latency verification against the MVP operating profile.
- Integration scenarios for restart recovery and deduplication.
- Final MVP acceptance verification.

## Milestones

### M0 Foundations Ready

Outcome:
- The repository boots through the canonical package.
- Docker and local runtime point to the same entrypoint contract.
- Dependencies, migrations, config loading, login entrypoint, logging, and health baseline are in place.
- Tests can run against the new project structure.

Exit criteria:
- The service starts and stops cleanly without placeholder code.
- Config validation fails fast on invalid env or YAML input.
- Config validation covers source and target identifier formats, queue sizes, `LOG_LEVEL`, `DRY_RUN`, normalization toggles, and login modes.
- Postgres connectivity and migration execution are wired.
- The login command creates or validates a session file path.

### M1 Intake To Candidate

Outcome:
- New source messages are read from Telegram, persisted once, normalized, filtered, and marked either `filtered_out` or `candidate`.

Exit criteria:
- Source-message deduplication works on `(source_chat_id, source_message_id)`.
- Filter behavior covers `any` and `all` modes.
- Filter behavior covers `case_insensitive` and normalization toggles from the YAML contract.
- Candidate classification persists `event_type`, `event_signal`, and `candidate_signature`.
- Queue-driven intake and processing operate end-to-end without publication.

### M2 Start Event Publish Slice

Outcome:
- Matching `start` candidates open events, suppress duplicates across sources, and publish the canonical message to the target channel.

Exit criteria:
- `first arrival wins` is enforced.
- Duplicate `start` candidates within the active window become `suppressed_duplicate`.
- Text publication works with attribution.
- `DRY_RUN` suppresses target-channel writes while preserving the same publish-decision path for verification.
- The first vertical slice is demoable end-to-end.

### M3 Full Event Lifecycle And Recovery

Outcome:
- The system handles `clear` signals, restart recovery, persisted candidate claiming, and publish failure state transitions.

Exit criteria:
- Matching `clear` closes an active event and is not published.
- Unmatched `clear` becomes `orphan_clear`.
- Restart recovery scans persisted `candidate`, `selected_for_publish`, and `publishing` rows and resumes work without duplicate publishing.
- Publish status and terminal failures are persisted on both message and event records.
- Transient publish failures follow the locked backoff policy and keep persisted retry state.

### M4 MVP Hardening

Outcome:
- The service meets the documented MVP acceptance bar for media support, resilience, and operability.

Exit criteria:
- Photo posts with captions are supported.
- Copy-forbidden fallback behaves deterministically.
- Flood-wait handling and retry behavior are covered.
- The service supports at least 100 configured sources on the target deployment profile.
- Normal end-to-end latency remains within 10 to 30 seconds when flood waits are not active.
- Runtime guidance covers secrets handling and reduced-privilege container operation.
- The documented manual acceptance scenarios pass.
- The runtime can be operated for 24 hours without manual intervention under normal conditions.

## Dependency Rules For Future Task Decomposition

- Break down work by milestone first, then by workstream.
- Every future task must map to one primary component owner and one acceptance signal.
- Do not create cross-component tasks unless the work is foundational, storage-related, or operational.
- Candidate aggregation remains the only place allowed to deduplicate candidates, manage event lifecycle, and create publication jobs.
- Publish behavior remains isolated to the publish worker and publisher adapter.
- Architecture invariants from this document must be treated as fixed defaults unless changed through an ADR.

## Test And Acceptance Matrix

The later task backlog must cover the following scenarios explicitly:

- invalid configuration fails at startup;
- startup works with an existing session file;
- one-time login works without a session file;
- duplicate source messages are ignored safely;
- include and exclude filters work in both `any` and `all` modes;
- normalization changes matching behavior only through the documented pipeline;
- `DRY_RUN` suppresses target publication without bypassing publish-decision logic;
- similar `start` messages within 5 minutes map to one event;
- a repeated `start` after 5 minutes opens a new event;
- `clear` closes only an active event of the same `event_type`;
- restart recovery resumes unprocessed `candidate`, `selected_for_publish`, and `publishing` rows safely;
- publish failures update persisted state correctly;
- transient publish retries follow the locked backoff policy;
- text and photo-with-caption flows satisfy the MVP acceptance bar.

## Out Of Scope For This Plan

- Detailed sprint slicing.
- Calendar estimates.
- Team staffing allocation.
- Post-MVP roadmap themes such as UI, multiple target channels, moderation, or external brokers.
