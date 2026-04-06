# M1 Normalization and filter engine

Planning ID: 0027
Status: Draft
Last updated: 2026-04-06

## Goal

Preserve the documented matching semantics for intake classification and formalize the stale-message rule before candidate persistence starts depending on filter results.

## Scope

- Implement the shared normalization pipeline for processing-owned text handling with NFKC, lowercasing, trimming, repeated-whitespace collapse, and `ё` to `е`.
- Evaluate include and exclude rules against both message text and media captions.
- Preserve `any`, `all`, and `first matching group wins` behavior from the configuration contract.
- Extend the YAML runtime contract with `classification_stale_after_seconds` and validate it as a required positive integer in both the typed model and the canonical config examples.
- Exclude queue consumption, direct row-state persistence, candidate signature generation, event deduplication, and publication behavior.

## Steps

1. Implement [M1 Normalization and filter engine: shared normalization helpers and toggle contract](tasks/01_0037_shared_normalization_helpers_and_toggle_contract.md) to define the reusable processing-owned normalization pipeline for NFKC, lowercasing, trimming, whitespace collapse, and `ё` to `е`.
2. Implement [M1 Normalization and filter engine: filter-group evaluation semantics](tasks/02_0038_filter_group_evaluation_semantics.md) to evaluate include and exclude rules in configuration order with the documented `any`, `all`, and first-matching-group behavior.
3. Implement [M1 Normalization and filter engine: runtime stale-classification contract extension](tasks/03_0039_runtime_stale_classification_contract_extension.md) to extend the typed YAML runtime contract and canonical examples with `runtime.classification_stale_after_seconds`.
4. Finish with [M1 Normalization and filter engine: normalization and filter verification](tasks/04_0040_normalization_and_filter_verification.md) to protect the shared text-normalization helpers, filter semantics, and config validation with focused tests.

## Risks

- Matching behavior can drift from the documented contract if normalization and regex evaluation are implemented separately in reader and processing code paths.
- Adding the stale rule as an implicit constant would hide an operator-facing runtime decision inside M1 implementation details.
- Combining filter-engine work and runtime-contract work in one story can blur ownership unless the deliverables are kept explicit in the steps and acceptance criteria.
- If group-order precedence is not tested explicitly, later changes can silently break the `first matching group wins` rule.

## Acceptance Criteria

- Filter behavior covers `any` and `all` modes across one or more filter groups.
- Include and exclude matching inspects both message text and media captions using the same shared normalization helpers that later feed persisted `normalized_text`.
- `case_insensitive` and normalization toggles change matching behavior only through the documented normalization pipeline.
- `runtime.classification_stale_after_seconds` is part of the canonical YAML runtime contract and examples, and fails validation when absent or invalid.
- Group-order precedence and the `all`-mode consistency rule remain enforced and testable, with runtime matching behavior verified separately from config semantic validation.
- An empty `exclude` list remains valid and behaves as no exclusion rules.

## Links

- Parent epic: [M1 Intake To Candidate](../0024_intake_to_candidate.md)
- Parent plan: [MVP Delivery Plan](../../2026-03-14-mvp-delivery-plan.md)
- Requirements: [Requirements](../../../../project/requirements.md)
- Architecture spec: [Architecture spec](../../../../project/architecture-spec.md)
- Depends on story: [M1 Intake state contract alignment](../01_0025_intake_state_contract_alignment/0025_intake_state_contract_alignment.md)
- Depends on story: [M0 Config and login contract](../../01_0001_foundations_ready/02_0007_config_login_contract/0007_config_login_contract.md)
