# M0: ініціалізація сховища: базова схема для записів повідомлень і подій

Status: Ready
Owner: TBD
Last updated: 2026-03-14

## Мета

Зафіксувати контракт довговічного стану MVP для `message_records` і `event_records`, щоб наступні milestones розширювали schema, а не знову відкривали фундаментальний дизайн persistence.

## Обсяг

- Визначити metadata SQLAlchemy Core для `message_records` і `event_records`.
- Закодувати зафіксовані для MVP message statuses, event states, publish statuses, foreign-key relation, timestamp fields і правила nullability.
- Додати першу ревізію Alembic, яка створює обидві таблиці разом із потрібними constraints та indexes.
- Винести за межі задачі repository APIs, startup readiness checks і бізнес-переходи стану за межами базового contract.

## Залежності

- [2026-03-14-task-m0-storage-bootstrap-storage-surface-alembic.md](2026-03-14-task-m0-storage-bootstrap-storage-surface-alembic.md)

## Кроки

1. Визначити table metadata SQLAlchemy Core для `message_records` і `event_records` у канонічному storage package.
2. Закодувати unique constraint на `(source_chat_id, source_message_id)` і базові lookup indexes зі специфікації архітектури.
3. Створити початкову ревізію Alembic для базової schema.
4. Перевірити, що revision відтворює той самий storage contract, який описаний планом поставки та специфікацією архітектури.

## Ризики

- Відсутність потрібних state fields зараз змусить наступні milestones переписувати базову лінію замість її розширення.
- Додавання зайвих таблиць або ORM models порушить зафіксовані storage defaults для MVP.

## Критерії приймання

- Канонічна metadata визначає `message_records` і `event_records` із зафіксованими для MVP полями й зв'язками.
- Початкова ревізія Alembic створює обидві таблиці, unique constraint на `(source_chat_id, source_message_id)` і потрібні lookup indexes.
- Базова schema використовує лише SQLAlchemy Core й не вводить ORM models або non-MVP tables.
- Чисту database можна змінювати до базової schema без ручних редагувань.

## Посилання

- Батьківський епік: [M0: готовність основ](2026-03-14-epic-m0-foundations-ready.md)
- Батьківська сторі: [M0: ініціалізація сховища](2026-03-14-story-m0-storage-bootstrap.md)
- Залежить від задачі: [2026-03-14-task-m0-storage-bootstrap-storage-surface-alembic.md](2026-03-14-task-m0-storage-bootstrap-storage-surface-alembic.md)
- Батьківський план: [2026-03-14-mvp-delivery-plan.md](2026-03-14-mvp-delivery-plan.md)
- Специфікація архітектури: [architecture-spec.md](../../project/architecture-spec.md)
