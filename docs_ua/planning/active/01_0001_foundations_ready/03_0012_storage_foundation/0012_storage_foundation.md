# M0: foundation для storage

Planning ID: 0012
Status: Draft
Last updated: 2026-03-15

## Мета

Визначити канонічний storage package, механізм migrations і довговічну базову schema, щоб наступні зрізи могли додавати persistence-поведінку без повторного відкриття foundational рішень щодо storage.

## Обсяг

- Використовувати PostgreSQL як канонічне довговічне сховище для MVP.
- Використовувати SQLAlchemy 2.x async engine і SQLAlchemy Core замість ORM models.
- Налаштувати Alembic як механізм schema migrations для сервісу.
- Визначити початкову базову schema навколо `message_records` і `event_records` з полями та зв'язками, потрібними наступним віхам.
- Зафіксувати канонічний surface storage package, який повинні повторно використовувати наступні роботи над repository і bootstrap.
- Non-goals: реалізація primitives repository, startup readiness hooks, wiring життєвого циклу runtime або feature-level storage behavior поза foundational contract.

## Кроки

1. Реалізувати [M0: foundation для storage: surface storage і каркас Alembic](tasks/01_0013_storage_surface_alembic.md), щоб зафіксувати канонічний surface storage package і каркас Alembic поверх контрактів runtime і config.
2. Продовжити [M0: foundation для storage: базова schema для записів повідомлень і подій](tasks/02_0014_schema_baseline.md), щоб визначити базову SQLAlchemy Core schema і першу ревізію Alembic для `message_records` і `event_records`.

## Ризики

- Введення ORM models створить зайву абстракцію, що не відповідає вже зафіксованому архітектурному вибору SQLAlchemy Core.
- Базова schema, яка пропустить ключові поля стану, може змусити наступні віхи знову відкривати persistence contract замість його розширення.
- Довільні межі storage modules тут змушуватимуть наступні сторі repository і bootstrap змінювати package contract замість того, щоб будуватися поверх нього.

## Критерії приймання

- PostgreSQL є єдиним підтримуваним канонічним довговічним сховищем для foundation storage MVP.
- Storage layer використовує SQLAlchemy async Core і не залежить від ORM models.
- Alembic під'єднано, і він може виконати початкову базову schema для `message_records` і `event_records`.
- Канонічний surface storage package є достатньо стабільним, щоб наступні сторі repository і runtime могли споживати його без перевизначення storage entrypoint.

## Посилання

- Батьківський епік: [M0: готовність основ](../0001_foundations_ready.md)
- Батьківський план: [План постачання MVP](../../2026-03-14-mvp-delivery-plan.md)
- Вимоги: [Вимоги](../../../../project/requirements.md)
- Специфікація архітектури: [Специфікація архітектури](../../../../project/architecture-spec.md)
- Залежить від сторі: [M0: контракт runtime і пакета](../01_0002_runtime_package_contract/0002_runtime_package_contract.md)
- Залежить від сторі: [M0: контракт конфігурації та login](../02_0007_config_login_contract/0007_config_login_contract.md)
- Downstream reference: [M0: контракт storage і readiness](../04_0015_storage_contract_readiness/0015_storage_contract_readiness.md) має повторно використовувати той самий contract engine, metadata і migrations, визначений цією story.
