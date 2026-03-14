# M0 Bootstrap, observability, and test harness

Status: Draft
Owner: Tech Lead
Last updated: 2026-03-14

## Goal

Make the canonical package bootable, observable, and testable so later slices can add runtime behavior without inventing lifecycle, health, or verification scaffolding midstream.

## Scope

- Define the service bootstrap sequence and graceful shutdown behavior for the canonical package.
- Create the queue and worker-registration boundaries that later stories will fill with concrete intake, processing, aggregation, and publish behavior.
- Establish structured JSON logging as the runtime default.
- Add a lightweight HTTP health endpoint with readiness semantics for Telegram, Postgres, and worker liveness at a high level.
- Establish the initial test harness for the canonical package layout, including bootstrap-oriented tests and fixtures.
- Non-goals: implement Telegram intake logic, business worker behavior, full integration suites, or capacity and latency verification.

## Steps

1. Define the canonical startup order for settings, storage, runtime queues, login/session readiness, worker registration, and health reporting.
2. Add graceful shutdown behavior so runtime components stop cleanly and leave clear operator-visible logs.
3. Establish the structured logging contract and a lightweight health endpoint that exposes readiness without promising deep diagnostics.
4. Create the baseline test harness for the canonical package so bootstrap, validation, and health behavior can be verified in automated tests.

## Risks

- Bootstrap ordering can become unstable if readiness checks and worker registration are interleaved without a clear lifecycle contract.
- Health reporting can give false confidence if it does not distinguish configuration success from Telegram readiness, database readiness, and worker liveness.
- Logging can become inconsistent if structured output is not defined before later stories start emitting runtime events.
- Test scaffolding can be too shallow to protect refactors if it does not anchor the canonical package and bootstrap entrypoints early.

## Acceptance Criteria

- The service starts and stops cleanly through the canonical package bootstrap path.
- Queue creation and worker-registration boundaries are explicit enough for later stories to attach concrete workers without changing bootstrap structure.
- Structured JSON logs are the default runtime output format.
- A lightweight health endpoint exposes readiness for Telegram, Postgres, and worker liveness at a high level.
- Automated tests can run against the canonical package layout and cover bootstrap-oriented behavior.

## Links

- Parent epic: [2026-03-14-epic-m0-foundations-ready.md](2026-03-14-epic-m0-foundations-ready.md)
- Parent plan: [2026-03-14-mvp-delivery-plan.md](2026-03-14-mvp-delivery-plan.md)
- Requirements: [../../project/requirements.md](../../project/requirements.md)
- Architecture spec: [../../project/architecture-spec.md](../../project/architecture-spec.md)
