# M1 Source intake and message deduplication: intake mapping and raw text surface

Planning ID: 0034
Status: Draft
Last updated: 2026-04-06

## Goal

Normalize Telethon message events into one canonical intake shape that later storage can persist without ambiguity about source metadata or text surface selection.

## Scope

- Map incoming Telethon message events into the persisted source-message fields.
- Capture source identifiers, minimal source metadata, media presence, and receive time.
- Define the `raw_text` convention as either the message text or the media caption surface.
- Exclude runtime subscription wiring, persistence mechanics, queue behavior, filter evaluation, and later processing states.

## Steps

1. Define the reader-owned mapping from Telethon message events to the canonical persisted intake fields.
2. Encode the `raw_text` selection rule so media-backed messages use the caption surface.
3. Keep the intake shape limited to fields required by later storage and publication work.

## Risks

- If the intake shape is too loose, later stories may infer conflicting source metadata or text selection rules.
- If mapping and persistence are mixed here, the reader will start owning storage decisions that belong in later tasks.

## Acceptance Criteria

- Telethon events map into one canonical intake record shape.
- `raw_text` consistently stores message text or media caption text.
- Source identifiers, metadata, media presence, and receive time are captured for later storage use.

## Links

- Parent epic: [M1 Intake To Candidate](../../0024_intake_to_candidate.md)
- Parent story: [M1 Source intake and message deduplication](../0026_source_intake_and_message_deduplication.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on task: [01_0033_telegram_source_subscription_and_adapter_boundary.md](01_0033_telegram_source_subscription_and_adapter_boundary.md)
- Depends on story: [M1 Intake state contract alignment](../../01_0025_intake_state_contract_alignment/0025_intake_state_contract_alignment.md)
