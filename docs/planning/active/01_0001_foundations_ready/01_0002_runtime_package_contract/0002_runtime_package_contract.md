# M0 Runtime and package contract

Planning ID: 0002
Status: Draft
Last updated: 2026-03-15

## Goal

Establish the canonical runtime and packaging contract under `src/telegram_aggregator/` so all later implementation work builds on one stable import, startup, dependency, and unit-test execution baseline.

## Scope

- Make `src/telegram_aggregator/` the only supported runtime package root for the MVP.
- Remove `src/Telegram-aggregator/` from the execution contract used by local and Docker startup paths.
- Define the canonical service and login entry modules expected by the MVP runtime.
- Align Docker and local invocation on the same module path and bootstrap contract.
- Establish a reproducible dependency baseline for runtime, migrations, configuration loading, health reporting, and test dependencies.
- Define one canonical unit-test execution contract for the canonical package layout.
- Create the package and module placeholders required by the architecture spec so later stories can implement concrete components without reshaping the package layout.
- Non-goals: implement Telegram intake, business workers, storage schema details beyond importable module boundaries, or feature-level logic.

## Steps

1. Implement [M0 Runtime and package contract: package skeleton and canonical entry modules](tasks/01_0003_package_skeleton_entrypoints.md) to create the canonical package tree, component placeholders, and stable service/login entry modules under `src/telegram_aggregator/`.
2. Implement [M0 Runtime and package contract: dependency baseline](tasks/02_0004_dependency_baseline.md) to lock one reproducible runtime, migration, config, observability, and test dependency surface for M0.
3. Implement [M0 Runtime and package contract: unit-test execution contract](tasks/03_0005_unit_test_execution_contract.md) to lock one supported command, discovery contract, and import expectation for unit tests against the canonical package layout.
4. Finish with [M0 Runtime and package contract: execution contract alignment](tasks/04_0006_execution_contract_alignment.md) to remove the legacy package from supported Docker and local startup paths after the canonical package and test surfaces are already fixed.

## Risks

- Hidden references to the legacy package name may remain in runtime assets and keep the old execution path alive.
- The package layout can drift from the architecture spec if placeholder modules are added ad hoc instead of following the locked component structure.
- A weak dependency baseline can unblock startup temporarily but still leave migrations or tests without a reproducible environment.
- Unit tests can remain nominally supported but operationally ambiguous if the story defines test dependencies without one canonical execution contract.
- Login bootstrap can diverge from service bootstrap if the entry modules do not share the same package contract from the start.

## Acceptance Criteria

- The repository boots through `src/telegram_aggregator/` rather than `src/Telegram-aggregator/`.
- Docker and local execution use the same service entrypoint contract.
- A canonical login entry module exists under `telegram_aggregator` and is compatible with the M0 login flow.
- The dependency baseline is explicit and reproducible for runtime, migration, and test dependency needs.
- One canonical repo-tracked unit-test execution contract exists for `src/telegram_aggregator/`.
- The package structure contains the component placeholders expected by the architecture spec.
- No repo-tracked runtime path still depends on the legacy package as the supported execution contract.

## Links

- Parent epic: [M0 Foundations Ready](../0001_foundations_ready.md)
- Parent plan: [MVP Delivery Plan](../../2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [Architecture spec](../../../../project/architecture-spec.md)
