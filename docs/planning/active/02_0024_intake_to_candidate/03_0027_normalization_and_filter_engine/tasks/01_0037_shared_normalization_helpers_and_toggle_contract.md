# M1 Normalization and filter engine: shared normalization helpers and toggle contract

Planning ID: 0037
Status: Draft
Last updated: 2026-04-06

## Goal

Define the reusable processing-owned normalization pipeline so later M1 classification can rely on one shared text transformation contract.

## Scope

- Implement the shared normalization helpers for text handling with NFKC, lowercasing, trimming, repeated-whitespace collapse, and `ё` to `е`.
- Keep the helpers controlled by the existing per-filter-group normalization and case-sensitivity toggles.
- Make the helpers reusable by later processing work without introducing queue consumption or persistence behavior.
- Exclude filter-group ordering, runtime config extensions, direct row-state persistence, candidate signature generation, event deduplication, and publication.

## Steps

1. Add the shared normalization helpers that implement the documented text transformation pipeline.
2. Wire the existing per-filter-group toggles into the helper contract so normalization behavior stays explicit.
3. Keep the helper API narrow enough for later processing code to reuse when persisting `normalized_text`.

## Risks

- Splitting normalization logic across reader and processing code paths would create subtle matching drift.
- Overloading the helper API with filter evaluation would blur ownership between normalization and classification.

## Acceptance Criteria

- The normalization pipeline covers NFKC, lowercasing, trimming, repeated-whitespace collapse, and `ё` to `е`.
- Existing per-filter-group toggles govern helper behavior through one reusable contract.
- Later processing code can reuse the helpers without importing queue or persistence concerns.

## Links

- Parent epic: [M1 Intake To Candidate](../../0024_intake_to_candidate.md)
- Parent story: [M1 Normalization and filter engine](../0027_normalization_and_filter_engine.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on story: [M1 Intake state contract alignment](../../01_0025_intake_state_contract_alignment/0025_intake_state_contract_alignment.md)
- Depends on story: [M1 Source intake and message deduplication](../../02_0026_source_intake_and_message_deduplication/0026_source_intake_and_message_deduplication.md)
