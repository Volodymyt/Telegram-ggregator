# M0: bootstrap, observability і тестовий каркас: harness верифікації bootstrap

Planning ID: 0023
Status: Ready
Last updated: 2026-03-15

## Мета

Захистити канонічний шлях bootstrap автоматизованою верифікацією і мінімальними спільними fixtures, сфокусованими на startup, shutdown, агрегації readiness і health behavior.

## Обсяг

- Додати bootstrap-oriented fixtures, stubs або helpers, потрібні для тестування runtime lifecycle в канонічному layout пакета.
- Перевірити успішний startup, propagation startup failures, graceful shutdown і health responses.
- Перевірити bootstrap behavior поверх спільних контрактів readiness storage і bootstrap Telegram без повторного тестування внутрішньої логіки storage.
- Винести за межі задачі storage migration tests, repository tests і end-to-end flows intake або publication.

## Кроки

1. Додати мінімальні спільні test helpers або fixtures, потрібні для перевірки канонічних bootstrap entrypoints і зареєстрованих runtime components.
2. Додати тести для успішного startup і propagation failures через провалідовані залежності config, readiness storage і readiness bootstrap Telegram.
3. Додати тести для graceful shutdown і меж життєвого циклу worker.
4. Додати тести health surface, які перевіряють агреговану readiness behavior без дублювання попередньої storage verification.

## Ризики

- Test fixtures можуть перетворитися на другу реалізацію bootstrap, якщо почнуть моделювати runtime behavior надто глибоко замість перевірки реального bootstrap contract.
- Ця задача легко продублює storage verification, якщо surface тестів не залишатиметься сфокусованою на життєвому циклі й агрегації readiness.

## Критерії приймання

- Automated tests покривають поведінку канонічного bootstrap для startup, shutdown і propagation failures.
- Automated tests покривають health responses, зібрані з readiness storage, readiness bootstrap Telegram і стану liveness worker.
- Спільні fixtures залишаються обмеженими bootstrap-oriented behavior і не забирають на себе storage-specific verification migrations або repository.
- Ця задача не розширюється до end-to-end тестування Telegram intake або publication.

## Посилання

- Батьківський епік: [M0: готовність основ](../../0001_foundations_ready.md)
- Батьківська сторі: [M0: bootstrap, observability і тестовий каркас](../0019_bootstrap_observability_test_harness.md)
- Батьківський план: [План постачання MVP](../../../2026-03-14-mvp-delivery-plan.md)
- Специфікація архітектури: [Специфікація архітектури](../../../../../project/architecture-spec.md)
- Залежить від задачі: [01_0020_runtime_lifecycle_queue_boundaries.md](01_0020_runtime_lifecycle_queue_boundaries.md)
- Залежить від задачі: [02_0021_telegram_client_bootstrap.md](02_0021_telegram_client_bootstrap.md)
- Залежить від задачі: [03_0022_observability_health_surface.md](03_0022_observability_health_surface.md)
- Залежить від задачі: [03_0018_verification_coverage.md](../../04_0015_storage_contract_readiness/tasks/03_0018_verification_coverage.md)
