# M0 Config and login contract

Planning ID: 0007
Status: Draft
Last updated: 2026-03-15

## Goal

Lock the operator-facing startup contract so configuration, validation, and login behavior fail fast and remain consistent across local and containerized execution.

## Scope

- Define the environment-variable contract for startup, including Telegram credentials, session path, database URL, target channel, config path, `LOG_LEVEL`, `DRY_RUN`, and `LOGIN`.
- Define the YAML contract for sources, filters, repost settings, and runtime queue-related settings needed at startup.
- Validate supported source identifiers as `@username`, `t.me/...`, or numeric identifiers where supported, and validate target identifiers as username or numeric identifier.
- Validate startup-relevant filter and runtime semantics, including `mode`, `case_insensitive`, normalization toggles, and queue sizes.
- Enforce the documented `all`-mode rule that all include rules share the same `event_type` and `event_signal`.
- Align `python -m telegram_aggregator.login` and `LOGIN=1` around one session-bootstrap contract and one session-path handling rule.
- Define actionable operator-facing failure semantics for invalid env, invalid YAML, unsupported identifier formats, and unusable session paths.
- Non-goals: implement business filtering logic, Telegram event handling, or publication behavior beyond the startup and login contract.

## Steps

1. Implement [M0 Config and login contract: startup settings boundary and env contract](tasks/01_0008_startup_settings_boundary.md) to load the operator-facing env surface and `CONFIG_PATH` once before runtime bootstrap continues.
2. Continue with [M0 Config and login contract: YAML contract models and file loading](tasks/02_0009_yaml_contract_models.md) to lock the typed file-based configuration shape for sources, filters, repost settings, and startup-relevant runtime sections.
3. Add [M0 Config and login contract: startup semantic validation and identifier rules](tasks/03_0010_startup_semantic_validation.md) to reject unsupported identifiers, inconsistent filter semantics, and invalid startup toggles with actionable errors.
4. Finish with [M0 Config and login contract: shared session bootstrap and login alignment](tasks/04_0011_login_session_bootstrap.md) to route `python -m telegram_aggregator.login` and `LOGIN=1` through one session-path and operator error contract.

## Risks

- Splitting validation across multiple modules can create drift between documented configuration rules and actual startup behavior.
- Identifier parsing can become inconsistent between source handling, target handling, and login flows if one shared validation path is not defined.
- The login command and `LOGIN=1` path can diverge in behavior if they do not share the same session-bootstrap logic.
- Weak startup errors can make operator failures hard to diagnose, especially when env and YAML problems appear together.

## Acceptance Criteria

- Invalid env or YAML input stops startup before the service enters steady-state bootstrap.
- Source and target identifier validation supports the documented input formats and rejects unsupported values with actionable errors.
- Validation covers `LOG_LEVEL`, `DRY_RUN`, queue sizes, normalization toggles, filter mode, and `all`-mode consistency for typed include rules.
- `python -m telegram_aggregator.login` creates or validates the session path and uses the same session rules as `LOGIN=1`.
- Session-path failures, config-shape failures, and identifier-format failures are surfaced distinctly enough for operators to correct them without code inspection.

## Links

- Parent epic: [M0 Foundations Ready](../0001_foundations_ready.md)
- Parent plan: [MVP Delivery Plan](../../2026-03-14-mvp-delivery-plan.md)
- Requirements: [Requirements](../../../../project/requirements.md)
- Architecture spec: [Architecture spec](../../../../project/architecture-spec.md)
