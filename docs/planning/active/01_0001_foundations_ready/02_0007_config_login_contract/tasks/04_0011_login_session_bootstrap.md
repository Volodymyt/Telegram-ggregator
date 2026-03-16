# M0 Config and login contract: shared session bootstrap and startup alignment

Planning ID: 0011
Status: Ready
Last updated: 2026-03-15

## Goal

Align the dedicated login entrypoint with normal startup session handling so session-path behavior and operator-visible failures stay consistent across local and containerized execution.

## Scope

- Route `python -m telegram_aggregator.login` through one shared login/session bootstrap flow that also defines the session-path rule used by normal startup.
- Reuse the canonical `AppConfig` boundary for session-related input instead of introducing path-specific parsing.
- Define one rule for creating, validating, and rejecting session paths across supported execution environments.
- Keep phone number, login code, and 2FA handling interactive by default and ensure passwords are not persisted in plain text through env, YAML, or source-controlled config.
- Exclude Telegram event handling, reconnect behavior, and broader service lifecycle orchestration.

## Steps

1. Define the shared session-bootstrap entry contract on top of the canonical `AppConfig` shape, including exactly which session-path checks it owns beyond simple path resolution.
2. Route the dedicated login entrypoint through the same session-path preparation and authorization boundary that normal startup depends on, without reopening env parsing outside `load_app_config()`.
3. Surface session-path failures distinctly from authorization failures and generic config errors.
4. Preserve normal startup with an existing session file while keeping explicit login bootstrap as the supported first-time authorization path.

## Risks

- `python -m telegram_aggregator.login` and normal startup session handling can diverge quickly if they keep separate bootstrap code paths.
- Session-path behavior can differ between local and containerized execution if directory-creation and path-validation rules are not locked here.
- Reopening a second config shape for login after adopting canonical `AppConfig` would recreate the same drift this task is meant to remove.
- Reintroducing phone or password env requirements here would weaken the interactive login contract and operator security posture.

## Acceptance Criteria

- `python -m telegram_aggregator.login` and normal startup session handling share one session-bootstrap contract.
- Session-path creation, parent-directory handling, validation, and failure handling follow the same rule for the dedicated login entrypoint and normal startup expectations.
- Session-path failures are surfaced distinctly from authorization failures and generic config-shape errors.
- The dedicated login entrypoint reuses canonical `AppConfig` loading, and phone/password prompts remain interactive instead of env-backed by default.

## Links

- Parent epic: [M0 Foundations Ready](../../0001_foundations_ready.md)
- Parent story: [M0 Config and login contract](../0007_config_login_contract.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Requirements: [Requirements](../../../../../project/requirements.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on task: [01_0008_startup_settings_boundary.md](01_0008_startup_settings_boundary.md)
- Depends on task: [03_0010_startup_semantic_validation.md](03_0010_startup_semantic_validation.md)
