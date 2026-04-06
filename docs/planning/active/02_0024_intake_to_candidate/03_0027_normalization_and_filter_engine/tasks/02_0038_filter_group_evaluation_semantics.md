# M1 Normalization and filter engine: filter-group evaluation semantics

Planning ID: 0038
Status: Draft
Last updated: 2026-04-06

## Goal

Implement the documented include and exclude evaluation rules so configuration order and group precedence stay deterministic before M1 classification consumes them.

## Scope

- Evaluate include and exclude rules against both message text and media captions.
- Preserve `any`, `all`, and first matching group wins behavior from the configuration contract.
- Keep evaluation separate from queue consumption, row-state persistence, runtime contract changes, and publication behavior.
- Exclude stale-classification contract work, direct candidate persistence, event deduplication, and publish logic.

## Steps

1. Implement configuration-ordered filter-group evaluation for include and exclude rules.
2. Apply the shared normalization helpers from the preceding task to both message text and media captions.
3. Preserve the documented `any`, `all`, and first matching group wins semantics without introducing runtime contract changes.

## Risks

- If group-order precedence is not explicit, later changes can silently alter which filter group wins.
- Allowing exclude handling to drift from include handling would fracture matching semantics across the same input surface.

## Acceptance Criteria

- Include and exclude matching work across both message text and media captions.
- `any`, `all`, and first matching group wins behavior remain deterministic and testable.
- Filter evaluation reuses the shared normalization helpers rather than duplicating text transformation logic.

## Links

- Parent epic: [M1 Intake To Candidate](../../0024_intake_to_candidate.md)
- Parent story: [M1 Normalization and filter engine](../0027_normalization_and_filter_engine.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on task: [01_0037_shared_normalization_helpers_and_toggle_contract.md](01_0037_shared_normalization_helpers_and_toggle_contract.md)
- Depends on story: [M1 Intake state contract alignment](../../01_0025_intake_state_contract_alignment/0025_intake_state_contract_alignment.md)
