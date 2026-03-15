# M0 Runtime and package contract: dependency baseline

Planning ID: 0004
Status: Done
Last updated: 2026-03-15

## Goal

Freeze one reproducible dependency baseline for M0 so runtime, config, storage, observability, migrations, and unit-test tooling all build on the same install surface.

## Scope

- Keep one pinned `requirements.txt` as the canonical dependency surface for local and Docker installs.
- Define the minimum baseline libraries required by the locked M0 architecture and downstream foundation stories.
- Cover runtime, config parsing, Postgres access, migrations, observability hooks, and unit-test dependencies in the same dependency baseline.
- Exclude the canonical unit-test command contract, migration content, bootstrap behavior, health endpoint implementation, and any switch to an installable package workflow such as `pyproject.toml`.

## Steps

1. Identify the minimum baseline libraries already implied by the architecture spec and active M0 stories.
2. Encode them in one reproducible `requirements.txt` surface rather than splitting runtime and test dependencies across parallel mechanisms.
3. Keep Docker and local setup aligned on the same dependency file and installation expectations.
4. Document the dependency baseline tightly enough that downstream M0 stories can reuse it without reopening packaging or test-dependency decisions.

## Risks

- A partial baseline can let startup imports pass while leaving migrations or tests without a reproducible environment.
- Introducing a second packaging mechanism now would reopen a decision that the story only needs to stabilize, not expand.
- Overloading this task with optional tooling would create churn before the runtime contract is even executable.

## Acceptance Criteria

- `requirements.txt` is the canonical M0 dependency baseline for Docker and local setup.
- The baseline is explicit enough for runtime imports, config parsing, migrations, observability hooks, and unit-test dependency installation or collection.
- Downstream M0 stories do not need to introduce a second dependency-install mechanism to proceed.
- The task does not add `pyproject.toml` or another parallel packaging contract.

## Links

- Parent epic: [M0 Foundations Ready](../../0001_foundations_ready.md)
- Parent story: [M0 Runtime and package contract](../0002_runtime_package_contract.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Followed by task: [03_0005_unit_test_execution_contract.md](03_0005_unit_test_execution_contract.md)
