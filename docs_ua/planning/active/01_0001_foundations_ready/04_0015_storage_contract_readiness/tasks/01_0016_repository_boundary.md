# M0: контракт storage і readiness: межа repository і примітиви збереження

Planning ID: 0016
Status: Ready
Last updated: 2026-03-15

## Мета

Визначити мінімальну стабільну межу persistence, яку наступні сторі reader, processing, aggregation і publish зможуть використовувати без перепроєктування storage layer.

## Обсяг

- Визначити межу repository для persistence повідомлень і подій, використовуючи лише SQLAlchemy Core.
- Реалізувати мінімальні persistence primitives, потрібні для створення, читання й оновлення `message_records` і `event_records`.
- Зробити ідемпотентне persistence повідомлень із джерел і явні transaction boundaries частиною storage contract.
- Винести за межі задачі candidate claiming, event deduplication, publish recovery та інші наступні бізнес-workflows.

## Кроки

1. Визначити repository modules або interfaces для persistence повідомлень і подій усередині канонічного storage package.
2. Реалізувати мінімальні read/write primitives поверх базової schema без вбудовування майбутніх бізнес-рішень у storage layer.
3. Зробити write-path повідомлень із джерел ідемпотентним за `(source_chat_id, source_message_id)`.
4. Експонувати transaction boundaries, які наступні сторі зможуть розширювати для змін стану candidate, event і publish.

## Ризики

- Надмірний дизайн repositories зараз протягне наступну бізнес-логіку в storage layer.
- Недостатньо чітка специфікація idempotency або transactions змусить наступні віхи знову відкривати storage contract.

## Критерії приймання

- Storage layer надає стабільну boundary repository для `message_records` і `event_records`.
- Перші persistence primitives можуть створювати, читати й оновлювати базові records поверх канонічної schema.
- Persistence повідомлень із джерел є явно ідемпотентним за `(source_chat_id, source_message_id)`.
- Layer repository використовує лише SQLAlchemy Core і не залежить від ORM models.

## Посилання

- Батьківський епік: [M0: готовність основ](../../0001_foundations_ready.md)
- Батьківська сторі: [M0: контракт storage і readiness](../0015_storage_contract_readiness.md)
- Батьківський план: [План постачання MVP](../../../2026-03-14-mvp-delivery-plan.md)
- Специфікація архітектури: [Специфікація архітектури](../../../../../project/architecture-spec.md)
- Залежить від задачі: [02_0014_schema_baseline.md](../../03_0012_storage_foundation/tasks/02_0014_schema_baseline.md)
