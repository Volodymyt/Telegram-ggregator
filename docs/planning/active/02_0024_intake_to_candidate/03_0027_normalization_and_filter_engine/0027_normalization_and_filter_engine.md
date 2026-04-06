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

1. Add the reusable normalization helpers that are controlled by the existing per-filter-group toggles and are later reused by the processing worker when persisting `normalized_text`.
2. Implement filter-group evaluation in configuration order with explicit handling for `any`, `all`, and exclude blocking.
3. Extend the typed YAML model, semantic validation, and canonical runtime examples with `runtime.classification_stale_after_seconds`.
4. Add focused verification for normalization toggles, caption matching, group-order precedence, runtime `all`-mode behavior, contract validation for `classification_stale_after_seconds`, and the empty-exclude-list edge case.

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
