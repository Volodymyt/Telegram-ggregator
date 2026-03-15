# M0 Config and login contract: YAML contract models and file loading

Planning ID: 0009
Status: Ready
Last updated: 2026-03-15

## Goal

Lock the file-based configuration shape and parsing path so startup consumes one typed YAML contract for sources, filters, repost options, and runtime settings.

## Scope

- Define typed YAML models for `sources`, `filters`, `repost`, and `runtime`.
- Parse the file at `CONFIG_PATH` through one canonical loading path reused by startup validation.
- Validate shape-level expectations for typed include rules, exclude rules, repost options, and startup-relevant runtime settings.
- Keep secrets and deployment-specific credentials outside the YAML contract.
- Exclude identifier-format validation, queue-size limits, `all`-mode consistency, and session-bootstrap behavior.

## Steps

1. Define the typed configuration models for the documented YAML sections and nested rule objects.
2. Load YAML from the resolved `CONFIG_PATH` and map parse failures to operator-facing config errors.
3. Validate required shape and field typing for sources, typed include rules, exclude rules, repost settings, and startup-relevant runtime sections.
4. Expose the parsed file configuration through the same canonical config boundary as env settings.

## Risks

- The YAML contract can drift from the documented requirements if shape validation is mixed with later semantic rules in ad hoc runtime modules.
- Allowing secrets into YAML would undermine the locked operator contract that keeps credentials in environment variables.
- Parse errors without field-oriented context would make operator correction slower than necessary.

## Acceptance Criteria

- The YAML contract matches the documented configuration shape for `sources`, `filters`, `repost`, and `runtime`.
- Malformed YAML or shape-level config errors stop startup before steady-state bootstrap begins.
- Startup code consumes one parsed file-config object instead of reparsing YAML in downstream modules.
- No second configuration source is introduced for values already owned by env input.

## Links

- Parent epic: [M0 Foundations Ready](../../0001_foundations_ready.md)
- Parent story: [M0 Config and login contract](../0007_config_login_contract.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Requirements: [Requirements](../../../../../project/requirements.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on task: [01_0008_startup_settings_boundary.md](01_0008_startup_settings_boundary.md)
