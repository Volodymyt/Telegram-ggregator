# M1 Normalization and filter engine: normalization and filter verification

Planning ID: 0040
Status: Draft
Last updated: 2026-04-06

## Goal

Protect the shared normalization helpers, filter semantics, and runtime contract extension with focused verification before M1 classification depends on them.

## Scope

- Add focused verification for normalization toggles, caption matching, group-order precedence, runtime `all`-mode behavior, and the empty-exclude-list edge case.
- Verify `runtime.classification_stale_after_seconds` validation through the typed model and semantic checks.
- Keep the test surface limited to normalization and filter-engine behavior.
- Exclude queue consumption, direct row-state persistence, candidate signature generation, event deduplication, and publication.

## Steps

1. Add tests that cover the shared normalization pipeline and the per-filter-group toggle behavior.
2. Add tests that cover include/exclude matching against both message text and media captions.
3. Add tests for group-order precedence, `any` and `all` behavior, and the empty-exclude-list edge case.
4. Add contract tests that cover `runtime.classification_stale_after_seconds` validation and canonical example coverage.

## Risks

- Test coverage that only checks happy paths could still miss precedence bugs or normalization drift.
- Mixing processing or persistence tests into this task would blur ownership and duplicate later M1 coverage.

## Acceptance Criteria

- Normalization behavior is covered by automated tests.
- Filter semantics are covered for text, captions, `any`, `all`, group order, and empty exclude lists.
- Runtime stale-classification validation is covered by automated tests.
- The verification scope stays limited to normalization and filter-engine contracts.

## Links

- Parent epic: [M1 Intake To Candidate](../../0024_intake_to_candidate.md)
- Parent story: [M1 Normalization and filter engine](../0027_normalization_and_filter_engine.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on task: [01_0037_shared_normalization_helpers_and_toggle_contract.md](01_0037_shared_normalization_helpers_and_toggle_contract.md)
- Depends on task: [02_0038_filter_group_evaluation_semantics.md](02_0038_filter_group_evaluation_semantics.md)
- Depends on task: [03_0039_runtime_stale_classification_contract_extension.md](03_0039_runtime_stale_classification_contract_extension.md)
