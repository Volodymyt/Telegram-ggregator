# M1 Intake state contract alignment: canonical schema metadata and relation surface

Planning ID: 0029
Status: Done
Last updated: 2026-05-02

## Goal

Define the canonical `tg_message` and `event` schema metadata for M1 so later storage, migration, and runtime work can rely on one locked persistence contract.

## Scope

- Define the `tg_message` and `event` table metadata with the canonical names used by M1.
- Split the message status surface into `classification_status`, `aggregation_status`, and `publish_status`.
- Rename the message-to-event relation surface from `event_record_id` to `event_id` everywhere inside the storage metadata contract.
- Preserve the idempotent source-message identity on `(source_chat_id, source_message_id)`.
- Exclude repository behavior, migration execution, startup readiness, and any reader or processing logic.

## Steps

1. Update the SQLAlchemy Core table definitions for `tg_message` and `event` to use the canonical M1 column names, nullability, constraints, and indexes.
2. Encode the split status fields and their locked value sets in the metadata layer without introducing runtime behavior.
3. Rename the relation metadata from `event_record_id` to `event_id`, including any FK, index, or constraint names that are part of the schema contract.
4. Confirm the metadata still expresses idempotent source-message identity on `(source_chat_id, source_message_id)`.

## Risks

- Leaving any legacy `message_records` or `event_records` names in the metadata would force later stories to carry two contracts at once.
- If the status axes are not split here, later processing stories will inherit an overloaded state model that conflicts with the delivery plan.
- Renaming the relation surface without matching metadata names would create a misleading contract even if the columns are correct.

## Acceptance Criteria

- The canonical persistence metadata exposes `tg_message` and `event`, not `message_records` or `event_records`.
- `tg_message` exposes `classification_status`, `aggregation_status`, and `publish_status` as distinct fields.
- The relation from `tg_message` to `event` is expressed as `event_id`, including metadata names that no longer mention `event_record_id`.
- The source-message identity remains defined on `(source_chat_id, source_message_id)`.

## Links

- Parent epic: [M1 Intake To Candidate](../../0024_intake_to_candidate.md)
- Parent story: [M1 Intake state contract alignment](../0025_intake_state_contract_alignment.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on task: [02_0014_schema_baseline.md](../../../01_0001_foundations_ready/03_0012_storage_foundation/tasks/02_0014_schema_baseline.md)
- Depends on task: [01_0016_repository_boundary.md](../../../01_0001_foundations_ready/04_0015_storage_contract_readiness/tasks/01_0016_repository_boundary.md)
