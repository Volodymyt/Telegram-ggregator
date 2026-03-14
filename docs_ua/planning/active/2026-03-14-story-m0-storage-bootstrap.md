# M0: ініціалізація сховища

Status: Draft
Owner: Tech Lead
Last updated: 2026-03-14

## Мета

Визначити PostgreSQL як виконувану базову лінію довговічного стану, щоб наступні зрізи могли зберігати повідомлення й події без повторного перегляду storage stack або migration contract.

## Обсяг

- Використовувати PostgreSQL як канонічне довговічне сховище для MVP.
- Використовувати async engine SQLAlchemy 2.x і SQLAlchemy Core замість ORM models.
- Налаштувати Alembic як механізм schema migration для сервісу.
- Визначити початкову базову схему навколо `message_records` і `event_records`, із полями та зв'язками, потрібними наступним milestones.
- Підключити до bootstrap перевірки з'єднання з database під час startup і виконання migration.
- Визначити межу repository layer, яку очікують наступні сторі reader, processing, aggregation і publish.
- Non-goals: імплементація повних бізнес-переходів стану, recovery loops або feature-level repositories поза bootstrap contract.

## Кроки

1. Визначити канонічний storage stack із PostgreSQL, async Core SQLAlchemy і Alembic.
2. Створити початкову базову migration для `message_records` і `event_records`, використовуючи внутрішні контракти, уже зафіксовані планом поставки.
3. Підключити з'єднання з database і виконання migration до startup, щоб readiness storage була відома до запуску runtime worker.
4. Визначити межу repository навколо збереження повідомлень і подій, щоб наступні сторі могли додавати поведінку без зміни storage contract.

## Декомпозиція задач

1. [M0: ініціалізація сховища: поверхня сховища та каркас Alembic](2026-03-14-task-m0-storage-bootstrap-storage-surface-alembic.md)
   Зафіксувати канонічну поверхню storage package і каркас Alembic поверх уже визначених контрактів runtime і config.
2. [M0: ініціалізація сховища: базова схема для записів повідомлень і подій](2026-03-14-task-m0-storage-bootstrap-schema-baseline.md)
   Визначити базову SQLAlchemy Core schema і першу ревізію Alembic для `message_records` і `event_records`.
3. [M0: ініціалізація сховища: межа репозиторію та примітиви збереження](2026-03-14-task-m0-storage-bootstrap-repository-boundary.md)
   Визначити мінімальний стабільний repository contract для збереження повідомлень і подій поверх базової схеми.
4. [M0: ініціалізація сховища: хуки готовності під час старту та міграцій](2026-03-14-task-m0-storage-bootstrap-startup-readiness-hooks.md)
   Додати єдиний шлях ініціалізації storage, який доводить досяжність database і коректність migration до запуску worker.
5. [M0: ініціалізація сховища: покриття верифікації](2026-03-14-task-m0-storage-bootstrap-verification-coverage.md)
   Захистити storage bootstrap contract автоматизованим покриттям для migrations, readiness і базових примітивів збереження.

## Послідовність виконання

1. Почати з [2026-03-14-task-m0-storage-bootstrap-storage-surface-alembic.md](2026-03-14-task-m0-storage-bootstrap-storage-surface-alembic.md), тому що всі інші storage-задачі залежать від канонічної поверхні пакета й каркаса Alembic.
2. Продовжити з [2026-03-14-task-m0-storage-bootstrap-schema-baseline.md](2026-03-14-task-m0-storage-bootstrap-schema-baseline.md), тому що schema і перша revision є довговічним контрактом для всієї подальшої роботи зі storage.
3. Потім реалізувати [2026-03-14-task-m0-storage-bootstrap-repository-boundary.md](2026-03-14-task-m0-storage-bootstrap-repository-boundary.md), тому що repository primitives мають працювати з реальними базовими таблицями й constraints.
4. Після цього реалізувати [2026-03-14-task-m0-storage-bootstrap-startup-readiness-hooks.md](2026-03-14-task-m0-storage-bootstrap-startup-readiness-hooks.md), тому що wiring startup має споживати той самий engine і migration contract, а не тимчасовий bootstrap-код.
5. Завершити [2026-03-14-task-m0-storage-bootstrap-verification-coverage.md](2026-03-14-task-m0-storage-bootstrap-verification-coverage.md), коли schema, repository і readiness contracts уже достатньо стабільні для спільної перевірки.

## Нотатки щодо послідовності

- Не починати цю сторі, доки сторі runtime package і config/login не зафіксують канонічний шлях пакета та контракт database settings.
- Задачі про межу repository і readiness під час startup можуть частково перекриватися лише після стабілізації задачі базової schema, але обидві мають споживати той самий engine, metadata і migration contract, створений першими двома задачами.
- Сторі про bootstrap і observability має споживати хук readiness storage, створений тут, а не перевизначати перевірки database.

## Ризики

- Введення ORM models створить зайву абстракцію, що не відповідає вже зафіксованому архітектурному вибору SQLAlchemy Core.
- Базова schema, яка пропустить ключові поля стану, може змусити наступні milestones знову відкривати persistence contracts замість їх розширення.
- Startup може стати крихким, якщо перевірки з'єднання і виконання migration не розрізнятимуть тимчасову недоступність database і помилки migration.
- Межі repository можуть стати надто широкими, якщо bootstrap спробує закодувати майбутню бізнес-логіку замість встановлення лише storage contract.

## Критерії приймання

- PostgreSQL є єдиним підтримуваним канонічним довговічним сховищем для шляху bootstrap MVP.
- Storage layer використовує async Core SQLAlchemy і не залежить від ORM models.
- Alembic підключено, і він може виконати початкову базову schema для `message_records` і `event_records`.
- Startup перевіряє з'єднання з database і завершується з чіткою помилкою, якщо з'єднання або виконання migration не є здоровими.
- Існує межа repository для збереження повідомлень і подій, на яку наступні сторі можуть спиратися без перепроєктування storage layer.

## Посилання

- Батьківський епік: [M0: готовність основ](2026-03-14-epic-m0-foundations-ready.md)
- Батьківський план: [2026-03-14-mvp-delivery-plan.md](2026-03-14-mvp-delivery-plan.md)
- Вимоги: [requirements.md](../../project/requirements.md)
- Специфікація архітектури: [architecture-spec.md](../../project/architecture-spec.md)
