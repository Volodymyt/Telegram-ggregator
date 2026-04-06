# M1 Source intake and message deduplication: Telegram source subscription and adapter boundary

Planning ID: 0033
Status: Draft
Last updated: 2026-04-06

## Goal

Wire configured Telegram sources through the canonical runtime path so intake starts from the approved bootstrap and adapter boundary instead of ad hoc reader wiring.

## Scope

- Register configured Telegram sources through the existing runtime and Telethon adapter boundary.
- Keep the reader startup path thin and separate from persistence and processing concerns.
- Preserve the canonical bootstrap contract introduced in M0.
- Exclude message mapping, persistence logic, queue enqueue behavior, filter evaluation, and any publish behavior.

## Steps

1. Attach source subscription to the canonical runtime startup path used by the reader.
2. Use the existing Telethon adapter boundary to subscribe to configured sources without introducing a parallel connection path.
3. Confirm the reader startup path still delegates lifecycle concerns to the shared bootstrap contract.

## Risks

- Bypassing the adapter boundary would make later intake and shutdown behavior harder to reason about.
- Pulling mapping or persistence into startup wiring would blur the ownership line between runtime bootstrap and reader intake.

## Acceptance Criteria

- Configured Telegram sources are subscribed through the canonical runtime path.
- The reader does not bypass the existing Telethon adapter boundary.
- Startup wiring remains thin and does not absorb persistence or processing logic.

## Links

- Parent epic: [M1 Intake To Candidate](../../0024_intake_to_candidate.md)
- Parent story: [M1 Source intake and message deduplication](../0026_source_intake_and_message_deduplication.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on story: [M0 Bootstrap, observability, and test harness](../../../01_0001_foundations_ready/05_0019_bootstrap_observability_test_harness/0019_bootstrap_observability_test_harness.md)
