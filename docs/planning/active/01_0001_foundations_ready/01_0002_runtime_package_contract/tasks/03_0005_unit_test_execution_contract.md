# M0 Runtime and package contract: unit-test execution contract

Planning ID: 0005
Status: Done
Last updated: 2026-03-15

## Goal

Lock one canonical way to run unit tests against `src/telegram_aggregator/` so downstream M0 stories can add coverage without reopening runner, discovery, or import-path expectations.

## Scope

- Define one supported unit-test runner and command for repo-tracked execution against the canonical package layout.
- Establish the minimum repo-tracked test-runner configuration or documentation needed for stable discovery and imports under `src/telegram_aggregator/`.
- Keep unit-test execution aligned with the dependency baseline already defined for M0.
- Make the unit-test contract explicit enough that later M0 stories can add tests without inventing a second execution path.
- Exclude feature-specific test cases, CI pipeline expansion, integration-test orchestration, and bootstrap or storage verification content owned by later stories.

## Steps

1. Choose the canonical unit-test invocation that exercises the canonical package layout and does not depend on the legacy package path.
2. Add the minimum repo-tracked runner configuration or documentation needed for stable discovery and imports.
3. Verify that the dependency baseline from task `03` is sufficient for the supported unit-test invocation.
4. Document the unit-test contract tightly enough that later M0 stories can add coverage without redefining runner or command semantics.

## Risks

- Leaving the unit-test runner implicit will force downstream stories to invent their own commands and import-path workarounds.
- Tying the unit-test contract too closely to one later feature story would reopen the runtime contract each time new coverage is added.
- Introducing multiple supported test commands during M0 would dilute the canonical package contract and create avoidable ambiguity.

## Acceptance Criteria

- One canonical repo-tracked command exists for running unit tests against `src/telegram_aggregator/`.
- The supported unit-test invocation resolves imports from `telegram_aggregator` without depending on `src/Telegram-aggregator/`.
- The unit-test contract is explicit enough that downstream M0 stories can add tests without choosing a new runner or alternate execution path.
- The task does not introduce CI-specific orchestration or a second supported test runner.

## Implementation Notes

- `pytest.ini` is the repo-tracked runner contract for M0 unit-test execution.
- The canonical unit-test command is `python -m pytest` from the repository root.
- Discovery is limited to `tests/unit/`, and `telegram_aggregator` imports resolve from `src/`.
- Async unit tests use `pytest-asyncio` in `strict` mode.
- `tests/unit/test_package_contract.py` provides a minimal smoke suite for import and async-runner verification.

## Links

- Parent epic: [M0 Foundations Ready](../../0001_foundations_ready.md)
- Parent story: [M0 Runtime and package contract](../0002_runtime_package_contract.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on task: [01_0003_package_skeleton_entrypoints.md](01_0003_package_skeleton_entrypoints.md)
- Depends on task: [02_0004_dependency_baseline.md](02_0004_dependency_baseline.md)
