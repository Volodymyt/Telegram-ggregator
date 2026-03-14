# M0: ініціалізація сховища: межа репозиторію та примітиви збереження

Status: Ready
Owner: TBD
Last updated: 2026-03-14

## Мета

Визначити мінімальну стабільну межу persistence, яку наступні сторі reader, processing, aggregation і publish зможуть використовувати без перепроєктування storage layer.

## Обсяг

- Визначити межу repository для збереження повідомлень і подій, використовуючи лише SQLAlchemy Core.
- Імплементувати мінімальні примітиви persistence, потрібні для створення, отримання та оновлення `message_records` і `event_records`.
- Зробити ідемпотентне збереження source-message і явні межі transaction частиною storage contract.
- Винести за межі задачі candidate claiming, deduplication подій, publish recovery та інші майбутні бізнес-workflows.

## Залежності

- [2026-03-14-task-m0-storage-bootstrap-schema-baseline.md](2026-03-14-task-m0-storage-bootstrap-schema-baseline.md)

## Кроки

1. Визначити repository modules або interfaces для збереження повідомлень і подій у межах канонічного storage package.
2. Імплементувати мінімальні read/write primitives поверх базової schema без вбудовування майбутніх бізнес-рішень у storage layer.
3. Зробити шлях запису source-message ідемпотентним за `(source_chat_id, source_message_id)`.
4. Відкрити межі transaction, які наступні сторі зможуть розширювати для змін стану candidate, event і publish.

## Ризики

- Надмірне проєктування repositories вже зараз потягне майбутню бізнес-логіку в storage layer.
- Недостатня специфікація ідемпотентності або transaction змусить наступні milestones знову відкривати storage contract.

## Критерії приймання

- Storage layer надає стабільну межу repository для `message_records` і `event_records`.
- Перші примітиви persistence можуть створювати, отримувати й оновлювати базові записи поверх канонічної schema.
- Збереження source-message явно є ідемпотентним за `(source_chat_id, source_message_id)`.
- Repository layer використовує лише SQLAlchemy Core і не залежить від ORM models.

## Посилання

- Батьківський епік: [M0: готовність основ](2026-03-14-epic-m0-foundations-ready.md)
- Батьківська сторі: [M0: ініціалізація сховища](2026-03-14-story-m0-storage-bootstrap.md)
- Залежить від задачі: [2026-03-14-task-m0-storage-bootstrap-schema-baseline.md](2026-03-14-task-m0-storage-bootstrap-schema-baseline.md)
- Батьківський план: [2026-03-14-mvp-delivery-plan.md](2026-03-14-mvp-delivery-plan.md)
- Специфікація архітектури: [architecture-spec.md](../../project/architecture-spec.md)
