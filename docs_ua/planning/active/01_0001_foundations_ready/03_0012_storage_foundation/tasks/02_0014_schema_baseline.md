# M0: foundation для storage: базова schema для записів повідомлень і подій

Planning ID: 0014
Status: Ready
Last updated: 2026-03-15

## Мета

Зафіксувати MVP-контракт довговічного стану для `message_records` і `event_records`, щоб наступні віхи розширювали schema, а не повторно відкривали foundational дизайн persistence.

## Обсяг

- Визначити SQLAlchemy Core metadata для `message_records` і `event_records`.
- Зафіксувати набори status для повідомлень, стани подій, status публікації, foreign-key relation, timestamp fields і правила nullability.
- Додати першу ревізію Alembic, яка створює обидві таблиці разом з потрібними constraints та indexes.
- Винести за межі задачі API repository, startup readiness checks і бізнес-переходи станів поза базовим contract.

## Кроки

1. Визначити SQLAlchemy Core table metadata для `message_records` і `event_records` у канонічному storage package.
2. Зафіксувати unique constraint на `(source_chat_id, source_message_id)` і базові lookup indexes із architecture spec.
3. Створити початкову ревізію Alembic для базової schema.
4. Переконатися, що ревізія створює той самий storage contract, який задокументовано в delivery plan і architecture spec.

## Ризики

- Відсутні status fields зараз змусять наступні віхи переписувати базову schema замість її розширення.
- Введення додаткових таблиць або ORM models порушить зафіксовані storage defaults MVP.

## Критерії приймання

- Канонічна metadata визначає `message_records` і `event_records` із зафіксованими полями та зв'язками MVP.
- Початкова ревізія Alembic створює обидві таблиці, unique constraint на `(source_chat_id, source_message_id)` і потрібні lookup indexes.
- Базова schema використовує лише SQLAlchemy Core і не вводить ORM models або не-MVP таблиці.
- Чисту database можна мігрувати до базової schema без ручних правок.

## Посилання

- Батьківський епік: [M0: готовність основ](../../0001_foundations_ready.md)
- Батьківська сторі: [M0: foundation для storage](../0012_storage_foundation.md)
- Батьківський план: [План постачання MVP](../../../2026-03-14-mvp-delivery-plan.md)
- Специфікація архітектури: [Специфікація архітектури](../../../../../project/architecture-spec.md)
- Залежить від задачі: [01_0013_storage_surface_alembic.md](01_0013_storage_surface_alembic.md)
