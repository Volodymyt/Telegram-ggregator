# M0: bootstrap, observability і тестовий каркас: surface observability і health

Planning ID: 0022
Status: Ready
Last updated: 2026-03-15

## Мета

Визначити observability surface runtime за замовчуванням, щоб оператори бачили readiness bootstrap на високому рівні без дублювання нижчорівневих перевірок storage або Telegram.

## Обсяг

- Визначити структуроване JSON-логування як формат output за замовчуванням для канонічних bootstrap entrypoints.
- Агрегувати high-level readiness з readiness storage, readiness bootstrap клієнта Telegram і liveness worker.
- Експонувати легку HTTP health endpoint або еквівалентну container health surface для канонічного runtime.
- Тримати health surface high-level і не йти в глибоку діагностику, backends метрик або feature-level event logging.
- Винести за межі задачі storage-specific health checks, якими вже володіє робота над readiness storage.

## Кроки

1. Визначити контракт структурованого логування за замовчуванням для подій startup, steady-state lifecycle і shutdown у канонічному bootstrap.
2. Змоделювати контракт агрегації readiness із readiness storage, readiness bootstrap клієнта Telegram і стану життєвого циклу worker.
3. Реалізувати легку health endpoint або еквівалентну container health surface, яка показує ці стани readiness на високому рівні.
4. Задокументувати межу між цією high-level health surface і глибшою діагностикою, зарезервованою для наступних віх.

## Ризики

- Health-звітність може створювати хибне відчуття надійності, якщо вона невдало дублюватиме нижчорівневі checks або змішуватиме readiness із глибшою операційною діагностикою.
- Логування може швидко стати непослідовним, якщо контракт JSON за замовчуванням не буде визначено до того, як наступні runtime-сторі почнуть emitting events.

## Критерії приймання

- Структуровані JSON-логи є runtime output за замовчуванням для канонічних bootstrap entrypoints.
- Health surface показує readiness bootstrap клієнта Telegram, readiness Postgres і liveness worker на високому рівні.
- Layer observability повторно використовує readiness hook storage і readiness signal bootstrap Telegram замість повторної реалізації цих checks.
- Ця задача не вводить глибоку діагностику, metrics infrastructure або feature-specific observability contracts.

## Посилання

- Батьківський епік: [M0: готовність основ](../../0001_foundations_ready.md)
- Батьківська сторі: [M0: bootstrap, observability і тестовий каркас](../0019_bootstrap_observability_test_harness.md)
- Батьківський план: [План постачання MVP](../../../2026-03-14-mvp-delivery-plan.md)
- Вимоги: [Вимоги](../../../../../project/requirements.md)
- Специфікація архітектури: [Специфікація архітектури](../../../../../project/architecture-spec.md)
- Залежить від задачі: [01_0020_runtime_lifecycle_queue_boundaries.md](01_0020_runtime_lifecycle_queue_boundaries.md)
- Залежить від задачі: [02_0021_telegram_client_bootstrap.md](02_0021_telegram_client_bootstrap.md)
- Залежить від задачі: [02_0017_startup_readiness_hooks.md](../../04_0015_storage_contract_readiness/tasks/02_0017_startup_readiness_hooks.md)
