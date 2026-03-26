# M0 Config and login contract: startup settings boundary and env contract

Planning ID: 0008
Status: Done
Last updated: 2026-03-16

## Goal

Establish one canonical startup settings boundary so service and login flows load operator-provided environment input once and fail fast before runtime wiring begins.

## Scope

- Define the canonical `src/telegram_aggregator/config/` surface for startup settings, path resolution, and config-file discovery.
- Parse required env vars `TG_API_ID`, `TG_API_HASH`, `TG_SESSION_PATH`, `DATABASE_URL`, `TARGET_CHANNEL`, and `CONFIG_PATH`, while allowing `TG_API_ID`, `TG_API_HASH`, and `TARGET_CHANNEL` to remain blank in the no-Telegram `DRY_RUN=1` bootstrap profile.
- Parse optional startup toggles `LOG_LEVEL` and `DRY_RUN` into the same typed boundary.
- Keep phone number, login code, and 2FA password out of the canonical env contract so later login flows can request them interactively.
- Validate startup-relevant paths early enough that later bootstrap code does not reopen env parsing or filesystem checks.
- Resolve `TG_SESSION_PATH` early, but leave parent-directory creation and session-file creation rules to the later shared session-bootstrap task.
- Make `DRY_RUN` disable Telegram client initialization entirely while preserving the non-Telegram startup boundary.
- Exclude YAML schema modeling, cross-field filter semantics, and session authorization behavior.

## Steps

1. Define the module boundary for env loading, path resolution, and startup settings exposure.
2. Parse required and optional env vars into typed startup settings without duplicating the logic in bootstrap entrypoints.
3. Fail fast on missing or malformed env input and unusable config-file paths before runtime bootstrap continues.
4. Document the shared startup-settings contract that later M0 tasks must reuse.

## Risks

- Duplicate env parsing in service and login entrypoints would reopen the operator contract immediately after it is defined.
- Validating config paths too late would allow runtime bootstrap to fail with less actionable errors than the config layer can provide.
- A settings object that already embeds runtime wiring concerns would make later bootstrap work harder to keep coherent.

## Acceptance Criteria

- One canonical startup-settings loader exists for the supported env surface.
- Missing or malformed required env input stops startup before the service enters steady-state bootstrap.
- Config-path failures are surfaced distinctly from later YAML-shape and semantic-validation failures.
- Later M0 stories can consume the shared startup-settings boundary without reparsing env input.
- `DRY_RUN` can enter runtime bootstrap without Telegram client initialization.
- The config boundary documents that the dry-run bootstrap profile may leave Telegram-facing values blank because no Telegram I/O occurs in that mode.

## Links

- Parent epic: [M0 Foundations Ready](../../0001_foundations_ready.md)
- Parent story: [M0 Config and login contract](../0007_config_login_contract.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Requirements: [Requirements](../../../../../project/requirements.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on story: [M0 Runtime and package contract](../../01_0002_runtime_package_contract/0002_runtime_package_contract.md)
