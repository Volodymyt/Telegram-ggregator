# M0 Bootstrap, observability, and test harness: Telegram client bootstrap and session readiness

Planning ID: 0021
Status: Ready
Last updated: 2026-03-15

## Goal

Add the minimum Telegram client bootstrap path so normal startup can validate or open the configured session and expose a narrow readiness signal without introducing reader behavior.

## Scope

- Define the bootstrap-facing Telethon client boundary that reuses the canonical session and login contract from M0 config work.
- Integrate Telegram client startup into the canonical runtime lifecycle defined by the bootstrap story.
- Add shutdown ownership for the Telegram client within the same runtime lifecycle.
- Expose a high-level Telegram client bootstrap readiness signal for health and observability consumption.
- Exclude source subscriptions, message handlers, and intake behavior.

## Steps

1. Define the bootstrap-facing client factory or adapter boundary that reuses the canonical session and login contract.
2. Integrate normal startup with existing-session validation and distinct operator-facing failures for missing or unusable session state.
3. Integrate Telegram client shutdown into the canonical runtime lifecycle.
4. Expose a narrow Telegram bootstrap readiness signal for later health and observability layers.

## Risks

- Telegram startup can drift from the canonical login path if session validation and operator-facing failure semantics are reimplemented here.
- A broad readiness model here could imply successful source subscription or reader startup before those contracts exist.

## Acceptance Criteria

- Normal startup reuses the canonical session and login contract and surfaces missing or unusable session failures distinctly.
- Telegram client start and stop are integrated into the canonical bootstrap lifecycle without attaching reader behavior.
- A narrow Telegram client bootstrap readiness signal exists for reuse by health and observability work.
- This task does not register source subscriptions or implement Telegram intake logic.

## Links

- Parent epic: [M0 Foundations Ready](../../0001_foundations_ready.md)
- Parent story: [M0 Bootstrap, observability, and test harness](../0019_bootstrap_observability_test_harness.md)
- Parent plan: [MVP Delivery Plan](../../../2026-03-14-mvp-delivery-plan.md)
- Requirements: [Requirements](../../../../../project/requirements.md)
- Architecture spec: [Architecture spec](../../../../../project/architecture-spec.md)
- Depends on story: [M0 Config and login contract](../../02_0007_config_login_contract/0007_config_login_contract.md)
- Depends on task: [01_0020_runtime_lifecycle_queue_boundaries.md](01_0020_runtime_lifecycle_queue_boundaries.md)
