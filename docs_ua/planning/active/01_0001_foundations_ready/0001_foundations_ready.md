# M0: готовність основ

Planning ID: 0001
Milestone: M0
Status: Active
Last updated: 2026-03-15

## Мета

Створити виконувану базову лінію MVP, щоб наступні зрізи могли додавати intake, aggregation і publication-поведінку без повторного відкриття рішень щодо runtime, storage чи операторського контракту.

## Обсяг

- Замінити застарілий execution path на канонічний корінь пакета `src/telegram_aggregator/`.
- Узгодити локальний і Docker runtime startup навколо одного контракту entrypoint.
- Зафіксувати env- і YAML-контракт конфігурації, включно з обома підтримуваними шляхами login.
- Визначити surface storage package, механізм migrations і початкову довговічну базову схему до того, як від них залежатиме wiring runtime.
- Додати мінімальну межу storage repository, startup readiness hooks, storage verification, порядок runtime bootstrap, керування життєвим циклом worker, структуроване логування, легку health-звітність і test scaffolding.
- Винести за межі цього етапу Telegram intake, оцінювання filters, candidate aggregation і publication-логіку поза інтерфейсами, потрібними для bootstrap сервісу.

## Кроки

1. Визначити канонічний пакет і runtime-контракт, щоб усі наступні сторі спиралися на однаковий шлях import і startup.
2. Описати й провалідувати env- і YAML-контракт, включно з сумісністю `LOGIN=1` і основним потоком `python -m telegram_aggregator.login`.
3. Зафіксувати канонічний surface storage package, інтеграцію Alembic і початкову довговічну базову схему.
4. Додати мінімальну межу storage repository, readiness hook для startup і storage verification, щоб runtime bootstrap споживав один стабільний storage contract.
5. Додати порядок bootstrap, readiness bootstrap клієнта Telegram, керування життєвим циклом, видимість health, структуровані logs і test scaffolding, щоб наступні зрізи були виконуваними й перевірюваними.

## Ризики

- Застарілий шлях `src/Telegram-aggregator/` може все ще використовуватися runtime- або container-артефактами й має перестати бути execution contract.
- Валідація config може розійтися з документованим контрактом, якщо parsing env, parsing YAML і обробка login будуть реалізовані незалежно.
- Робота над storage foundation може все ще протікати в наступні зрізи, якщо рішення щодо schema і migrations змішати з рішеннями про repository і runtime readiness в одному delivery slice.
- Health і test scaffolding можуть виявитися надто поверхневими, якщо вони недостатньо чітко показуватимуть readiness bootstrap клієнта Telegram, readiness Postgres і liveness worker.

## Критерії приймання

- Репозиторій запускається через канонічний пакет під `src/telegram_aggregator/`, і жоден підтримуваний локальний або Docker startup path більше не використовує `src/Telegram-aggregator/` як runtime contract.
- Docker і локальний runtime використовують один і той самий контракт entrypoint сервісу та однакові очікування щодо startup.
- Базова лінія dependencies є явною й відтворюваною для runtime, migrations, завантаження configuration, observability і тестів.
- Сервіс чисто запускається і зупиняється через канонічний шлях bootstrap без placeholder runtime loops.
- Валідація config швидко завершується помилкою на невалідному env або YAML input до входу сервісу в steady-state startup.
- Валідація config покриває формати source і target identifier, розміри queue, `LOG_LEVEL`, `DRY_RUN`, перемикачі normalization, семантику режиму filter, включно з документованим правилом узгодженості режиму `all`, і обидва підтримувані режими login.
- Обидва підтримувані шляхи входу виконувані й узгоджені навколо одного session-bootstrap contract: звичайний startup працює з наявним session file, а і `LOGIN=1`, і `python -m telegram_aggregator.login` створюють або перевіряють налаштований шлях сесії з окремими operator-facing помилками при збої.
- Підключення до PostgreSQL, виконання migrations і одна початкова довговічна базова схема під'єднані через один канонічний storage path до того, як від нього залежатиме runtime bootstrap.
- Storage layer надає мінімальну межу repository і один повторно використовуваний readiness hook, потрібний для подальшої роботи reader, processing, aggregation, publish і bootstrap, без повторного відкриття storage contract.
- Створення queue, межі реєстрації worker і порядок bootstrap визначені достатньо явно, щоб наступні сторі могли під'єднувати конкретні worker без зміни M0 runtime structure.
- Структуровані JSON-логи є форматом runtime output за замовчуванням.
- Легка health endpoint або еквівалентна container health surface показує readiness bootstrap клієнта Telegram, Postgres і liveness worker на високому рівні.
- Automated tests запускаються проти канонічного layout пакета і покривають bootstrap-орієнтовану поведінку, валідацію config, роботу login/session і storage foundation разом з очікуваннями readiness storage.

## Посилання

- Батьківський план: [План постачання MVP](../2026-03-14-mvp-delivery-plan.md)
- Вимоги: [Вимоги](../../../project/requirements.md)
- Специфікація архітектури: [Специфікація архітектури](../../../project/architecture-spec.md)
- Сторі: [M0: контракт runtime і пакета](01_0002_runtime_package_contract/0002_runtime_package_contract.md)
- Сторі: [M0: контракт конфігурації та login](02_0007_config_login_contract/0007_config_login_contract.md)
- Сторі: [M0: foundation для storage](03_0012_storage_foundation/0012_storage_foundation.md)
- Сторі: [M0: контракт storage і readiness](04_0015_storage_contract_readiness/0015_storage_contract_readiness.md)
- Сторі: [M0: bootstrap, observability і тестовий каркас](05_0019_bootstrap_observability_test_harness/0019_bootstrap_observability_test_harness.md)
