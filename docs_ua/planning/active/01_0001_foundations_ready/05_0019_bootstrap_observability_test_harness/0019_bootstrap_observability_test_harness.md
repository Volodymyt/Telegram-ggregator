# M0: bootstrap, observability і тестовий каркас

Planning ID: 0019
Status: Draft
Last updated: 2026-03-15

## Мета

Зробити канонічний пакет таким, що запускається, спостерігається і тестується, щоб наступні зрізи могли додавати runtime-поведінку без вигадування lifecycle, bootstrap Telegram або verification scaffolding посеред роботи.

## Обсяг

- Визначити послідовність bootstrap сервісу та поведінку graceful shutdown для канонічного пакета.
- Додати мінімальну інтеграцію bootstrap клієнта Telegram і session-readiness, потрібну для звичайного startup і operator-visible health.
- Створити межі queue і реєстрації worker, які наступні сторі заповнять конкретною логікою intake, processing, aggregation і publish.
- Зробити структуроване JSON-логування форматом runtime за замовчуванням.
- Додати легку HTTP health endpoint із семантикою readiness для bootstrap клієнта Telegram, Postgres і liveness worker на високому рівні.
- Закласти bootstrap-орієнтований test harness для канонічного layout пакета без перевизначення storage-specific verification, яке належить попереднім сторі.
- Non-goals: реалізація логіки Telegram intake, бізнес-поведінки worker, повних integration suites або перевірок capacity і latency.

## Кроки

1. Реалізувати [M0: bootstrap, observability і тестовий каркас: життєвий цикл runtime і межі queue](tasks/01_0020_runtime_lifecycle_queue_boundaries.md), щоб визначити канонічний порядок startup, ownership queue, межу реєстрації worker і контракт graceful shutdown у `bootstrap/`.
2. Продовжити [M0: bootstrap, observability і тестовий каркас: bootstrap клієнта Telegram і readiness сесії](tasks/02_0021_telegram_client_bootstrap.md), щоб інтегрувати мінімальний path startup і shutdown Telethon у канонічний runtime lifecycle без додавання reader behavior.
3. Реалізувати [M0: bootstrap, observability і тестовий каркас: surface observability і health](tasks/03_0022_observability_health_surface.md), щоб зробити структуровані JSON-логи і high-level readiness видимими поверх спільних контрактів bootstrap і storage.
4. Завершити [M0: bootstrap, observability і тестовий каркас: harness верифікації bootstrap](tasks/04_0023_bootstrap_verification_harness.md), щоб захистити поведінку startup, shutdown і health без дублювання storage-specific verification.

## Ризики

- Порядок bootstrap може стати нестабільним, якщо readiness checks і реєстрація worker будуть переплетені без чіткого lifecycle contract.
- Health-звітність може створювати хибне відчуття надійності, якщо вона не розрізнятиме успіх конфігурації, readiness bootstrap клієнта Telegram, readiness database і liveness worker.
- Логування може швидко стати непослідовним, якщо структурований output не буде визначено до того, як наступні сторі почнуть виводити runtime events.
- Test scaffolding може дублювати попереднє storage coverage, якщо ця сторі не залишатиметься прив'язаною до bootstrap entrypoints, health і concerns життєвого циклу.

## Критерії приймання

- Сервіс чисто запускається і зупиняється через канонічний шлях bootstrap пакета.
- Звичайний startup інтегрує канонічний session/login contract із мінімальним шляхом bootstrap клієнта Telegram, який наступні runtime-сторі зможуть розширити без зміни структури startup M0.
- Межі створення queue і реєстрації worker визначені достатньо явно, щоб наступні сторі могли під'єднати конкретні worker без зміни структури bootstrap.
- Структуровані JSON-логи є форматом runtime output за замовчуванням.
- Легка health endpoint показує readiness bootstrap клієнта Telegram, Postgres і liveness worker на високому рівні.
- Automated tests запускаються проти канонічного layout пакета і покривають bootstrap-орієнтовану поведінку без повторного привласнення storage-specific acceptance, уже покритого раніше в M0.

## Посилання

- Батьківський епік: [M0: готовність основ](../0001_foundations_ready.md)
- Батьківський план: [План постачання MVP](../../2026-03-14-mvp-delivery-plan.md)
- Вимоги: [Вимоги](../../../../project/requirements.md)
- Специфікація архітектури: [Специфікація архітектури](../../../../project/architecture-spec.md)
- Залежить від сторі: [M0: контракт конфігурації та login](../02_0007_config_login_contract/0007_config_login_contract.md)
- Залежить від сторі: [M0: контракт storage і readiness](../04_0015_storage_contract_readiness/0015_storage_contract_readiness.md)
- Обмеження послідовності: [M0: bootstrap, observability і тестовий каркас: surface observability і health](tasks/03_0022_observability_health_surface.md) починається лише після стабілізації [M0: bootstrap, observability і тестовий каркас: життєвий цикл runtime і межі queue](tasks/01_0020_runtime_lifecycle_queue_boundaries.md), [M0: bootstrap, observability і тестовий каркас: bootstrap клієнта Telegram і readiness сесії](tasks/02_0021_telegram_client_bootstrap.md) і storage readiness hook із [M0: контракт storage і readiness: readiness startup і migration hooks](../04_0015_storage_contract_readiness/tasks/02_0017_startup_readiness_hooks.md).
- Обмеження послідовності: [M0: bootstrap, observability і тестовий каркас: harness верифікації bootstrap](tasks/04_0023_bootstrap_verification_harness.md) починається лише після стабілізації задач `01`-`03` і має повторно використовувати storage-specific verification з [M0: контракт storage і readiness: покриття верифікації](../04_0015_storage_contract_readiness/tasks/03_0018_verification_coverage.md), а не дублювати його.
