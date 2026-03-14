# M0 Storage bootstrap: verification coverage

Status: Ready
Owner: TBD
Last updated: 2026-03-14

## Goal

Protect the storage bootstrap contract with automated verification so later M0 and M1 work does not regress migrations, readiness checks, or baseline persistence behavior.

## Scope

- Add automated verification for the baseline Alembic revision.
- Verify the first repository primitives against the canonical schema, including idempotent source-message persistence.
- Verify that storage initialization distinguishes connectivity failures from migration failures.
- Exclude later business workflow tests for candidate recovery, deduplication, and publication behavior.

## Dependencies

- [2026-03-14-task-m0-storage-bootstrap-schema-baseline.md](2026-03-14-task-m0-storage-bootstrap-schema-baseline.md)
- [2026-03-14-task-m0-storage-bootstrap-repository-boundary.md](2026-03-14-task-m0-storage-bootstrap-repository-boundary.md)
- [2026-03-14-task-m0-storage-bootstrap-startup-readiness-hooks.md](2026-03-14-task-m0-storage-bootstrap-startup-readiness-hooks.md)

## Steps

1. Add migration smoke coverage for the initial Alembic revision.
2. Add repository tests for baseline create, fetch, update, and idempotent source-message persistence behavior.
3. Add readiness tests that prove storage initialization distinguishes connectivity failures from migration failures.
4. Keep the verification surface limited to storage bootstrap expectations.

## Risks

- Without automated coverage, the storage contract will regress quietly as later milestones add runtime behavior.
- Test scope can become noisy if it starts covering future candidate or publish workflows before those contracts exist.

## Acceptance Criteria

- Automated verification covers the baseline migration path.
- Automated verification covers the first repository primitives on `message_records` and `event_records`.
- Automated verification proves that storage readiness distinguishes connectivity failures from migration failures.
- The verification scope stays limited to storage bootstrap behavior.

## Links

- Parent epic: [2026-03-14-epic-m0-foundations-ready.md](2026-03-14-epic-m0-foundations-ready.md)
- Parent story: [2026-03-14-story-m0-storage-bootstrap.md](2026-03-14-story-m0-storage-bootstrap.md)
- Depends on task: [2026-03-14-task-m0-storage-bootstrap-schema-baseline.md](2026-03-14-task-m0-storage-bootstrap-schema-baseline.md)
- Depends on task: [2026-03-14-task-m0-storage-bootstrap-repository-boundary.md](2026-03-14-task-m0-storage-bootstrap-repository-boundary.md)
- Depends on task: [2026-03-14-task-m0-storage-bootstrap-startup-readiness-hooks.md](2026-03-14-task-m0-storage-bootstrap-startup-readiness-hooks.md)
- Parent plan: [2026-03-14-mvp-delivery-plan.md](2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [../../project/architecture-spec.md](../../project/architecture-spec.md)
