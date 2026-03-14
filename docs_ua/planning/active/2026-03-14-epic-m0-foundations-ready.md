# M0: готовність основ

Status: Active
Owner: Tech Lead
Last updated: 2026-03-14

## Мета

Створити виконувану базову лінію MVP, щоб наступні зрізи могли додавати intake, aggregation і publication-поведінку без повторного перегляду рішень щодо runtime, storage чи операторського контракту.

## Обсяг

- Замінити застарілий шлях виконання на канонічний корінь пакета `src/telegram_aggregator/`.
- Узгодити локальний і Docker startup runtime навколо одного контракту entrypoint.
- Зафіксувати контракт конфігурації env і YAML, включно з обома підтримуваними шляхами login.
- Підключити перевірку з'єднання з PostgreSQL, виконання migration і початкову довговічну базову схему.
- Додати runtime bootstrap, керування життєвим циклом worker, структуроване logging, легку health-звітність і тестовий каркас.
- Винести за межі цього етапу Telegram intake, обчислення filter, агрегацію candidate і логіку publication поза інтерфейсами, потрібними для bootstrap сервісу.

## Поточний стан

- `Dockerfile` досі запускає `python -m Telegram-aggregator`.
- `requirements.txt` досі є заглушкою.
- `src/telegram_aggregator/` ще не містить цільових runtime-модулів.
- Репозиторію все ще потрібні канонічний шлях bootstrap, шар config, шар storage, базова observability і test harness.

## Мапа сторі

1. [M0: контракт runtime і пакета](2026-03-14-story-m0-runtime-package-contract.md)
2. [M0: контракт конфігурації та login](2026-03-14-story-m0-config-login-contract.md)
3. [M0: ініціалізація сховища](2026-03-14-story-m0-storage-bootstrap.md)
4. [M0: bootstrap, observability і тестовий каркас](2026-03-14-story-m0-bootstrap-observability-test-harness.md)

## Кроки

1. Визначити канонічний пакет і runtime-контракт, щоб усі наступні сторі спиралися на однаковий шлях import і startup.
2. Описати й провалідувати контракт env і YAML, включно з сумісністю `LOGIN=1` та основним потоком `python -m telegram_aggregator.login`.
3. Підключити PostgreSQL і Alembic до bootstrap з мінімальною, але довговічною базовою схемою.
4. Додати керування життєвим циклом, видимість health, структуровані logs і test scaffolding, щоб наступні зрізи були виконуваними та перевірюваними.

## Ризики

- Застарілий шлях `src/Telegram-aggregator/` може досі використовуватися runtime- або container-артефактами й має перестати бути execution contract.
- Валідація config може розійтися з документованим контрактом, якщо parsing env, parsing YAML і обробка login будуть реалізовані незалежно.
- Bootstrap storage може зробити startup крихким, якщо збої з'єднання та migration не завершуватимуться швидко з окремими operator-facing помилками.
- Health і test scaffolding можуть виявитися надто поверхневими, якщо вони недостатньо чітко відображатимуть готовність Telegram, готовність Postgres і liveness worker.

## Критерії приймання

- Репозиторій запускається через канонічний пакет.
- Docker і локальний runtime вказують на один і той самий контракт entrypoint.
- Налаштовано dependencies, migrations, завантаження config, login entrypoint, logging і базову health-перевірку.
- Тести можна запускати проти нової структури проєкту.
- Сервіс коректно запускається і зупиняється без placeholder-коду.
- Валідація config швидко завершується помилкою на невалідному env або YAML input.
- Валідація config покриває формати source і target identifier, розміри queue, `LOG_LEVEL`, `DRY_RUN`, перемикачі normalization та режими login.
- Підключено перевірку з'єднання з Postgres і виконання migration.
- Команда login створює або валідує шлях до session-файлу.

## Посилання

- Батьківський план: [2026-03-14-mvp-delivery-plan.md](2026-03-14-mvp-delivery-plan.md)
- Вимоги: [requirements.md](../../project/requirements.md)
- Специфікація архітектури: [architecture-spec.md](../../project/architecture-spec.md)
