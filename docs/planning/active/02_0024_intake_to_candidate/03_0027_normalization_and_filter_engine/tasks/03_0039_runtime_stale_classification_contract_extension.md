# M1 Normalization and filter engine: runtime stale-classification contract extension

Planning ID: 0039
Status: Draft
Last updated: 2026-04-06

## Goal

Extend the typed runtime contract so stale-classification behavior is explicit, validated, and visible in canonical examples before processing uses it.

## Scope

- Add `runtime.classification_stale_after_seconds` to the typed YAML runtime contract.
- Validate it as a required positive integer in the typed model and semantic checks.
- Update canonical runtime examples so the operator-facing contract includes the stale-classification window.
- Exclude filter evaluation internals, queue consumption, direct row-state persistence, candidate signature generation, event deduplication, and publication.

## Steps

1. Extend the typed YAML model with `runtime.classification_stale_after_seconds`.
2. Add semantic validation that rejects missing or invalid stale-classification values.
3. Refresh the canonical runtime examples to document the new required runtime field.

## Risks

- Making the stale rule implicit would hide an operator-facing decision inside implementation details.
- Changing config semantics without corresponding examples would make the contract harder to validate and maintain.

## Acceptance Criteria

- `runtime.classification_stale_after_seconds` is part of the canonical YAML runtime contract.
- Missing, zero, or otherwise invalid values fail validation.
- Canonical runtime examples include the stale-classification window.

## Links

- Parent epic: [M1 Intake To Candidate](../../0024_intake_to_candidate.md)
- Parent story: [M1 Normalization and filter engine](../0027_normalization_and_filter_engine.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on story: [M0 Config and login contract](../../01_0001_foundations_ready/02_0007_config_login_contract/0007_config_login_contract.md)
