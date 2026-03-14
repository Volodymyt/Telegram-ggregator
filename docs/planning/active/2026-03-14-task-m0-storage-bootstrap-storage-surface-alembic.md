# M0 Storage bootstrap: storage surface and Alembic scaffold

Status: Ready
Owner: TBD
Last updated: 2026-03-14

## Goal

Lock one canonical storage entrypoint for the MVP so schema, repositories, and bootstrap logic build on the same PostgreSQL and Alembic integration surface.

## Scope

- Add the `src/telegram_aggregator/storage/` package skeleton for engine creation, metadata registration, migration execution, and storage-specific error types.
- Add the Alembic project files required by the canonical package layout.
- Wire Alembic to the SQLAlchemy Core metadata owned by the storage package.
- Reuse the M0 runtime and config contracts for dependency wiring and `DATABASE_URL` access rather than creating a parallel settings path.
- Exclude schema field design, repository behavior, and full runtime bootstrap wiring.

## Dependencies

- [2026-03-14-story-m0-runtime-package-contract.md](2026-03-14-story-m0-runtime-package-contract.md)
- [2026-03-14-story-m0-config-login-contract.md](2026-03-14-story-m0-config-login-contract.md)

## Steps

1. Create the `storage/` package structure and define the canonical modules for engine creation, metadata exposure, migrations, and storage errors.
2. Add Alembic configuration files under the repository root and point them at the canonical storage metadata.
3. Ensure the storage package consumes the existing M0 configuration boundary for `DATABASE_URL`.
4. Document the import and execution contract that later storage tasks must reuse.

## Risks

- Alembic can drift from runtime storage configuration if it resolves database settings through a separate path.
- Ad hoc module naming here would force later storage tasks to reshape the package boundary.

## Acceptance Criteria

- `src/telegram_aggregator/storage/` exists as the canonical storage package surface.
- Alembic is present in the repo and resolves the canonical SQLAlchemy Core metadata without ad hoc wiring.
- Storage initialization depends on the shared M0 config contract for database settings.
- No second storage bootstrap path is introduced outside the canonical package.

## Links

- Parent epic: [2026-03-14-epic-m0-foundations-ready.md](2026-03-14-epic-m0-foundations-ready.md)
- Parent story: [2026-03-14-story-m0-storage-bootstrap.md](2026-03-14-story-m0-storage-bootstrap.md)
- Parent plan: [2026-03-14-mvp-delivery-plan.md](2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [../../project/architecture-spec.md](../../project/architecture-spec.md)
