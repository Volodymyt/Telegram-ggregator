# M0 Runtime and package contract: package skeleton and canonical entry modules

Planning ID: 0003
Status: Ready
Last updated: 2026-03-15

## Goal

Lock the canonical package tree and entry-module contract under `src/telegram_aggregator/` so later M0 stories can add config, storage, and bootstrap behavior without reshaping imports or startup paths.

## Scope

- Create the canonical `src/telegram_aggregator/` package root and the component package placeholders required by the architecture spec.
- Add stable service and login entry modules that route into the canonical bootstrap package contract.
- Define the minimum bootstrap-module placeholders needed so the entry modules import through one stable runtime surface.
- Treat `src/Telegram-aggregator/` as legacy scaffolding and exclude any new implementation work under that path.
- Exclude config validation, Telegram session handling, storage readiness, worker lifecycle behavior, and health reporting.

## Steps

1. Create the importable package skeleton under `src/telegram_aggregator/` with the component directories already locked by the architecture spec.
2. Add `__main__.py` as the canonical service entry module and `login.py` as the canonical login entry module.
3. Route both entry modules through stable bootstrap-facing module boundaries instead of embedding future runtime logic directly in the top-level package files.
4. Keep the package placeholders thin and importable so later stories can fill them in without renaming modules or moving directories.

## Risks

- Ad hoc placeholder naming here would force later stories to reopen the canonical package contract.
- Embedding runtime behavior directly in the entry modules would make config and bootstrap work harder to extend cleanly.
- Leaving ambiguous ownership between `__main__.py`, `login.py`, and `bootstrap/` can cause the service and login flows to diverge before the runtime contract stabilizes.

## Acceptance Criteria

- `src/telegram_aggregator/` exists as the only supported MVP runtime package root.
- The component package placeholders from the architecture spec are present and importable under the canonical package.
- `python -m telegram_aggregator` and `python -m telegram_aggregator.login` resolve through canonical entry modules under `telegram_aggregator`.
- No new implementation surface is introduced under `src/Telegram-aggregator/`.

## Links

- Parent epic: [M0 Foundations Ready](../../0001_foundations_ready.md)
- Parent story: [M0 Runtime and package contract](../0002_runtime_package_contract.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
