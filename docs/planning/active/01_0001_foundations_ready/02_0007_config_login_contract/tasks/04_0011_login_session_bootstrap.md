# M0 Config and login contract: shared session bootstrap and login alignment

Planning ID: 0011
Status: Ready
Last updated: 2026-03-15

## Goal

Align both supported login entry paths on one session-bootstrap contract so session-path handling and operator-visible failures stay consistent across local and containerized execution.

## Scope

- Route `python -m telegram_aggregator.login` and `LOGIN=1` through one shared login/session bootstrap flow.
- Reuse the canonical startup settings and validation boundaries for session-related input instead of introducing path-specific parsing.
- Define one rule for creating, validating, and rejecting session paths across supported execution environments.
- Keep 2FA handling interactive and ensure passwords are not persisted in plain text through env, YAML, or source-controlled config.
- Exclude Telegram event handling, reconnect behavior, and broader service lifecycle orchestration.

## Steps

1. Define the shared session-bootstrap entry contract, including the minimal validated settings it requires.
2. Route both supported login entry paths through the same session-path preparation and authorization boundary.
3. Surface session-path failures distinctly from authorization failures and generic config errors.
4. Preserve normal startup with an existing session file while keeping explicit login bootstrap as the supported first-time authorization path.

## Risks

- `LOGIN=1` and `python -m telegram_aggregator.login` can diverge quickly if they keep separate bootstrap code paths.
- Session-path behavior can differ between local and containerized execution if directory-creation and path-validation rules are not locked here.
- Forcing login bootstrap to depend on unrelated full-service config would create avoidable operator friction when only session authorization is needed.

## Acceptance Criteria

- `python -m telegram_aggregator.login` and `LOGIN=1` share one session-bootstrap contract.
- Session-path creation, validation, and failure handling follow the same rule across both supported login entry paths.
- Session-path failures are surfaced distinctly from authorization failures and generic config-shape errors.
- Normal startup remains compatible with an existing session file, and 2FA passwords are not stored in plain text.

## Links

- Parent epic: [M0 Foundations Ready](../../0001_foundations_ready.md)
- Parent story: [M0 Config and login contract](../0007_config_login_contract.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Requirements: [Requirements](../../../../../project/requirements.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on task: [01_0008_startup_settings_boundary.md](01_0008_startup_settings_boundary.md)
- Depends on task: [03_0010_startup_semantic_validation.md](03_0010_startup_semantic_validation.md)
