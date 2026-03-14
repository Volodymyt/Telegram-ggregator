# M0 Runtime and package contract

Status: Draft
Last updated: 2026-03-14

## Goal

Establish the canonical runtime and packaging contract under `src/telegram_aggregator/` so all later implementation work builds on one stable import, startup, and dependency baseline.

## Scope

- Make `src/telegram_aggregator/` the only supported runtime package root for the MVP.
- Remove `src/Telegram-aggregator/` from the execution contract used by local and Docker startup paths.
- Define the canonical service and login entry modules expected by the MVP runtime.
- Align Docker and local invocation on the same module path and bootstrap contract.
- Establish a reproducible dependency baseline for runtime, migrations, configuration loading, health reporting, and tests.
- Create the package and module placeholders required by the architecture spec so later stories can implement concrete components without reshaping the package layout.
- Non-goals: implement Telegram intake, business workers, storage schema details beyond importable module boundaries, or feature-level logic.

## Steps

1. Introduce the canonical package structure under `src/telegram_aggregator/` with stable entry modules for service bootstrap and login bootstrap.
2. Remove the legacy package from all runtime-facing startup paths, including Docker and any documented local invocation contract.
3. Define the minimum dependency baseline needed for the service runtime, migrations, configuration parsing, observability, and tests.
4. Add importable package placeholders for the component layout already locked in the architecture spec.

## Risks

- Hidden references to the legacy package name may remain in runtime assets and keep the old execution path alive.
- The package layout can drift from the architecture spec if placeholder modules are added ad hoc instead of following the locked component structure.
- A weak dependency baseline can unblock startup temporarily but still leave migrations or tests without a reproducible environment.
- Login bootstrap can diverge from service bootstrap if the entry modules do not share the same package contract from the start.

## Acceptance Criteria

- The repository boots through `src/telegram_aggregator/` rather than `src/Telegram-aggregator/`.
- Docker and local execution use the same service entrypoint contract.
- A canonical login entry module exists under `telegram_aggregator` and is compatible with the M0 login flow.
- The dependency baseline is explicit and reproducible for runtime, migration, and test needs.
- The package structure contains the component placeholders expected by the architecture spec.
- No repo-tracked runtime path still depends on the legacy package as the supported execution contract.

## Links

- Parent epic: [M0 Foundations Ready](../epic.md)
- Parent plan: [MVP Delivery Plan](../../2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [Architecture spec](../../../../project/architecture-spec.md)
