# M0 Storage contract and readiness: verification coverage

Planning ID: 0018
Status: Ready
Last updated: 2026-03-15

## Goal

Protect the storage contract and readiness behavior with automated verification so later M0 and M1 work does not regress migrations, readiness checks, or baseline persistence behavior.

## Scope

- Add automated verification for the baseline Alembic revision.
- Verify the first repository primitives against the canonical schema, including idempotent source-message persistence.
- Verify that storage initialization distinguishes connectivity failures from migration failures.
- Exclude later business workflow tests for candidate recovery, deduplication, and publication behavior.

## Steps

1. Add migration smoke coverage for the initial Alembic revision.
2. Add repository tests for baseline create, fetch, update, and idempotent source-message persistence behavior.
3. Add readiness tests that prove storage initialization distinguishes connectivity failures from migration failures.
4. Keep the verification surface limited to storage contract and readiness expectations.

## Risks

- Without automated coverage, the storage contract will regress quietly as later milestones add runtime behavior.
- Test scope can become noisy if it starts covering future candidate or publish workflows before those contracts exist.

## Acceptance Criteria

- Automated verification covers the baseline migration path.
- Automated verification covers the first repository primitives on `message_records` and `event_records`.
- Automated verification proves that storage readiness distinguishes connectivity failures from migration failures.
- The verification scope stays limited to storage contract and readiness behavior.

## Links

- Parent epic: [M0 Foundations Ready](../../0001_foundations_ready.md)
- Parent story: [M0 Storage contract and readiness](../0015_storage_contract_readiness.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on task: [02_0014_schema_baseline.md](../../03_0012_storage_foundation/tasks/02_0014_schema_baseline.md)
- Depends on task: [01_0016_repository_boundary.md](01_0016_repository_boundary.md)
- Depends on task: [02_0017_startup_readiness_hooks.md](02_0017_startup_readiness_hooks.md)
