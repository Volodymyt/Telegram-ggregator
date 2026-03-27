# M0 Config and login contract: startup semantic validation and identifier rules

Planning ID: 0010
Status: Done
Last updated: 2026-03-16

## Goal

Enforce startup semantic validation before runtime initialization so unsupported identifiers and inconsistent config semantics fail with actionable operator-facing errors.

## Scope

- Validate supported source identifiers as `@username`, `t.me/...`, or numeric identifiers where supported, and validate target identifiers as username or numeric identifier.
- Validate `LOG_LEVEL`, `DRY_RUN`, queue sizes, per-group filter-mode values, and normalization-related toggles used at startup.
- Enforce the documented `all`-mode rule that all typed include rules inside one filter group share the same `event_type` and `event_signal`.
- Surface distinct operator-facing validation failures for env values, YAML semantics, and identifier formats.
- Exclude Telethon authorization flow and broader runtime worker bootstrap.

## Steps

1. Add shared validation primitives for supported source and target identifier formats.
2. Validate startup semantics for log level, booleans, queue sizes, and normalization-related toggles.
3. Enforce per-group filter-mode semantics, including the `all`-mode consistency rule for typed include rules inside each filter group.
4. Stop startup before runtime initialization when semantic validation fails and preserve actionable error context for operators.

## Risks

- Identifier parsing can drift between source handling and target handling if one shared validation path is not defined here.
- Delaying semantic validation until runtime wiring would produce partial bootstrap states and harder-to-diagnose failures.
- Collapsing all semantic failures into a single opaque config error would weaken the operator contract that this story is meant to lock.

## Acceptance Criteria

- Source and target identifier validation supports the documented input formats and rejects unsupported values with actionable errors.
- Validation covers `LOG_LEVEL`, `DRY_RUN`, queue sizes, normalization toggles, per-group filter mode, and `all`-mode consistency for typed include rules inside each filter group.
- Semantic validation failures stop startup before the service enters runtime initialization.
- Operators can distinguish env-value, YAML-semantic, and identifier-format failures without code inspection.

## Links

- Parent epic: [M0 Foundations Ready](../../0001_foundations_ready.md)
- Parent story: [M0 Config and login contract](../0007_config_login_contract.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Requirements: [Requirements](../../../../../project/requirements.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on task: [01_0008_startup_settings_boundary.md](01_0008_startup_settings_boundary.md)
- Depends on task: [02_0009_yaml_contract_models.md](02_0009_yaml_contract_models.md)
