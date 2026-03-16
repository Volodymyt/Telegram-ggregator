# M0 Runtime and package contract: execution contract alignment

Planning ID: 0006
Status: Done
Last updated: 2026-03-15

## Goal

Remove the legacy package from the supported execution contract so Docker and local startup both advertise and consume one canonical runtime path.

## Scope

- Update repo-tracked Docker and local startup assets to invoke the canonical service entrypoint under `telegram_aggregator`.
- Remove `src/Telegram-aggregator/` from supported startup documentation and runtime-facing command examples.
- Decide whether the legacy package remains temporarily as an unsupported shim or is removed entirely, but keep it outside the supported MVP contract either way.
- Keep the service and login module paths aligned with the package skeleton defined by the runtime contract.
- Exclude full bootstrap implementation, login/session behavior, and deeper operability guidance beyond the supported invocation contract.

## Steps

1. Audit repo-tracked runtime assets and docs that still reference `Telegram-aggregator` as a supported execution path.
2. Update Docker and documented local startup paths to use `python -m telegram_aggregator`.
3. Remove or clearly demote the legacy package from the supported contract without creating a second canonical path.
4. Verify that later M0 stories can reference one supported module path for runtime startup.

## Risks

- Hidden legacy references in Docker or run instructions can keep the old execution contract alive even after the canonical package exists.
- Supporting both package names at the documentation layer would create avoidable operator confusion during M0.
- Cleaning up the legacy path too aggressively could break non-supported local habits unless the supported contract is documented clearly first.

## Acceptance Criteria

- No supported repo-tracked Docker or local startup path still uses `python -m Telegram-aggregator`.
- Docker and local runtime documentation point to the same canonical service module path.
- The legacy package, if still present, is no longer described as a supported MVP execution path.
- The canonical login path remains `python -m telegram_aggregator.login` and is not redefined elsewhere.

## Implementation Notes

- `docker-compose.yml` makes the canonical service command explicit with `python -m telegram_aggregator`.
- `README.md` documents the supported local operator flows as `docker compose up app` for service startup and `docker compose run --rm app python -m telegram_aggregator.login` for login.
- The repository no longer contains `src/Telegram-aggregator/`, so the legacy package is fully outside the supported MVP execution contract.

## Links

- Parent epic: [M0 Foundations Ready](../../0001_foundations_ready.md)
- Parent story: [M0 Runtime and package contract](../0002_runtime_package_contract.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on task: [01_0003_package_skeleton_entrypoints.md](01_0003_package_skeleton_entrypoints.md)
