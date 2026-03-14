# Backlog

This document stores prioritized work that is not yet active.

## Status Model

Use one of the following statuses for each item:

- `Draft`
- `Ready`
- `Blocked`
- `Done`
- `Archived`

## Planning Item Types

- `Epic`: A large outcome-oriented planning item that groups related stories.
- `Story`: A testable delivery slice within one epic that can be decomposed into tasks.
- `Task`: The smallest execution item within one story that describes concrete implementation work.

Use the hierarchy `epic > story > task` during decomposition.

## Title Lineage Convention

Encode ancestor relationships directly in the item title by using planning directory IDs in square brackets.

```md
- [Status] Epic title
- [Status][m0_01_foundations_ready] Story title
- [Status][m0_01_foundations_ready][03_storage_bootstrap] Task title
```

- Use only ancestor directory IDs, without filenames or parent paths.
- Order bracket segments from the highest ancestor to the nearest ancestor.
- Do not include the current item's own directory ID or task filename in its title.
- If an ancestor does not have its own planning directory yet, omit that bracket segment until the directory exists.

## Item Template

Use a compact format for each backlog item:

```md
- [Status][ancestor-dir-id-1][ancestor-dir-id-2] Short title
  - Type: Epic | Story | Task
  - Why it matters:
  - Acceptance signal:
  - Links:
```

## Maintenance Rule

- Keep the list prioritized from top to bottom.
- Keep title lineage aligned with current planning directory IDs when linked ancestor planning directories exist.
- Move active execution plans into [`active/`](active/README.md).
- Move completed or superseded work into [`archive/`](archive/README.md).

## Prioritized Items

These items intentionally omit lineage brackets until separate epic or story planning files exist.

Current active execution focus: [M0 Foundations Ready](active/m0_01_foundations_ready/epic.md).

### M1

- [Draft] M1 Intake To Candidate
  - Type: Epic
  - Why it matters: Deliver the first durable slice from Telegram intake to candidate state without publication.
  - Acceptance signal: The M1 exit criteria in the MVP delivery plan are satisfied.
  - Links: [MVP delivery plan](active/2026-03-14-mvp-delivery-plan.md)

- [Draft] M1 Source intake and message deduplication
  - Type: Story
  - Why it matters: Ensure source messages are read once, persisted once, and safely ignored on duplicate delivery.
  - Acceptance signal: Telethon reads configured sources, persists incoming messages once, and deduplicates on `(source_chat_id, source_message_id)`.
  - Links: Parent epic: M1 Intake To Candidate; [MVP delivery plan](active/2026-03-14-mvp-delivery-plan.md)

- [Draft] M1 Normalization and filter engine
  - Type: Story
  - Why it matters: Preserve the documented matching semantics for include and exclude rules before candidate classification starts.
  - Acceptance signal: Filter behavior covers `any` and `all` modes plus `case_insensitive` and normalization toggles against message text and media captions.
  - Links: Parent epic: M1 Intake To Candidate; [MVP delivery plan](active/2026-03-14-mvp-delivery-plan.md)

- [Draft] M1 Candidate classification pipeline
  - Type: Story
  - Why it matters: Convert accepted messages into durable candidate state with the metadata needed for later event aggregation.
  - Acceptance signal: Queue-driven processing persists either `filtered_out` or `candidate` together with `event_type`, `event_signal`, and `candidate_signature`.
  - Links: Parent epic: M1 Intake To Candidate; [MVP delivery plan](active/2026-03-14-mvp-delivery-plan.md)

### M2

- [Draft] M2 Start Event Publish Slice
  - Type: Epic
  - Why it matters: Deliver the first demoable end-to-end MVP path from `start` candidate to target-channel publication.
  - Acceptance signal: The M2 exit criteria in the MVP delivery plan are satisfied.
  - Links: [MVP delivery plan](active/2026-03-14-mvp-delivery-plan.md)

- [Draft] M2 Start event opening
  - Type: Story
  - Why it matters: Introduce the canonical event-opening rule that decides which message becomes the publication source.
  - Acceptance signal: Matching `start` candidates open events with `first arrival wins` and the selected message becomes the canonical source.
  - Links: Parent epic: M2 Start Event Publish Slice; [MVP delivery plan](active/2026-03-14-mvp-delivery-plan.md)

- [Draft] M2 Duplicate suppression window
  - Type: Story
  - Why it matters: Prevent repeated publication across sources while preserving the documented five-minute reopen rule.
  - Acceptance signal: Similar `start` candidates within the active window become `suppressed_duplicate`, while a matching `start` after five minutes opens a new event.
  - Links: Parent epic: M2 Start Event Publish Slice; [MVP delivery plan](active/2026-03-14-mvp-delivery-plan.md)

- [Draft] M2 Text publication and dry run
  - Type: Story
  - Why it matters: Provide the first operator-visible outcome without relaxing the publish-path and attribution requirements.
  - Acceptance signal: The serialized publish worker sends text posts with attribution, and `DRY_RUN` suppresses target writes while preserving the same publication decision path.
  - Links: Parent epic: M2 Start Event Publish Slice; [MVP delivery plan](active/2026-03-14-mvp-delivery-plan.md)

### M3

- [Draft] M3 Full Event Lifecycle And Recovery
  - Type: Epic
  - Why it matters: Make the event model restart-safe and operationally reliable beyond the first publish slice.
  - Acceptance signal: The M3 exit criteria in the MVP delivery plan are satisfied.
  - Links: [MVP delivery plan](active/2026-03-14-mvp-delivery-plan.md)

- [Draft] M3 Clear signal lifecycle
  - Type: Story
  - Why it matters: Complete the event lifecycle by closing active events without publishing clear messages.
  - Acceptance signal: Matching `clear` signals close only active events of the same `event_type`, while unmatched clears become `orphan_clear`.
  - Links: Parent epic: M3 Full Event Lifecycle And Recovery; [MVP delivery plan](active/2026-03-14-mvp-delivery-plan.md)

- [Draft] M3 Candidate recovery and claiming
  - Type: Story
  - Why it matters: Resume interrupted aggregation work safely after restart without duplicate event processing.
  - Acceptance signal: Persisted `candidate` rows are reclaimed transactionally and resume processing safely after restart.
  - Links: Parent epic: M3 Full Event Lifecycle And Recovery; [MVP delivery plan](active/2026-03-14-mvp-delivery-plan.md)

- [Draft] M3 Publication recovery and retry state
  - Type: Story
  - Why it matters: Preserve publish intent and retry semantics across process restarts and transient Telegram failures.
  - Acceptance signal: Rows left in `selected_for_publish` or `publishing` are rebuilt into publication jobs, and retries follow the locked `5s`, `15s`, `30s`, `60s`, then capped `300s` backoff policy.
  - Links: Parent epic: M3 Full Event Lifecycle And Recovery; [MVP delivery plan](active/2026-03-14-mvp-delivery-plan.md)

- [Draft] M3 Terminal failure state transitions
  - Type: Story
  - Why it matters: Make non-retriable publish failures explicit and queryable in both message and event state.
  - Acceptance signal: Non-retriable publish failures mark the message as `publish_failed` and the owning event as `failed` without further retries.
  - Links: Parent epic: M3 Full Event Lifecycle And Recovery; [MVP delivery plan](active/2026-03-14-mvp-delivery-plan.md)

### M4

- [Draft] M4 MVP Hardening
  - Type: Epic
  - Why it matters: Raise the service from first-slice correctness to the full MVP acceptance bar.
  - Acceptance signal: The M4 exit criteria in the MVP delivery plan are satisfied.
  - Links: [MVP delivery plan](active/2026-03-14-mvp-delivery-plan.md)

- [Draft] M4 Photo and caption publication
  - Type: Story
  - Why it matters: Expand the publish slice to the minimum media support required by the MVP.
  - Acceptance signal: Photo posts with captions are supported while album handling remains on the first-message strategy for the MVP.
  - Links: Parent epic: M4 MVP Hardening; [MVP delivery plan](active/2026-03-14-mvp-delivery-plan.md)

- [Draft] M4 Copy-forbidden and flood-wait resilience
  - Type: Story
  - Why it matters: Keep publish behavior deterministic under Telegram-specific delivery constraints.
  - Acceptance signal: Copy-forbidden publication falls back to deterministic `link_only` attribution text, and `FloodWaitError` sleeps for the exact reported duration before retrying the same job.
  - Links: Parent epic: M4 MVP Hardening; [MVP delivery plan](active/2026-03-14-mvp-delivery-plan.md)

- [Draft] M4 Capacity and latency verification
  - Type: Story
  - Why it matters: Prove that the service remains within the documented MVP operating envelope.
  - Acceptance signal: The service supports at least 100 configured sources and keeps normal end-to-end latency within 10 to 30 seconds on the target VPS profile when flood waits are not active.
  - Links: Parent epic: M4 MVP Hardening; [MVP delivery plan](active/2026-03-14-mvp-delivery-plan.md)

- [Draft] M4 Operator hardening and final acceptance
  - Type: Story
  - Why it matters: Finish the MVP with deployable runtime guidance and explicit acceptance coverage.
  - Acceptance signal: Runtime guidance covers secrets handling and reduced-privilege containers, manual acceptance scenarios pass, and the service can operate for 24 hours without manual intervention under normal conditions.
  - Links: Parent epic: M4 MVP Hardening; [MVP delivery plan](active/2026-03-14-mvp-delivery-plan.md)
