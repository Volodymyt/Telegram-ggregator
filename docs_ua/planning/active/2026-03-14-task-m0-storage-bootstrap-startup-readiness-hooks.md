# M0: ініціалізація сховища: хуки готовності під час старту та міграцій

Status: Ready
Owner: TBD
Last updated: 2026-03-14

## Мета

Надати єдиний шлях ініціалізації storage, який доводить досяжність Postgres і коректність migration до того, як почнуть працювати runtime worker.

## Обсяг

- Імплементувати ініціалізацію storage, яка відкриває async engine, перевіряє з'єднання з database і виконує або валідує migrations під час startup.
- Розрізняти operator-facing помилки недоступності database і збоїв виконання migration.
- Експортувати вузький readiness contract, який можуть споживати шари bootstrap і health.
- Винести за межі задачі загальне керування життєвим циклом worker і реалізацію health endpoint, які належать сторі bootstrap.

## Залежності

- [2026-03-14-task-m0-storage-bootstrap-storage-surface-alembic.md](2026-03-14-task-m0-storage-bootstrap-storage-surface-alembic.md)
- [2026-03-14-task-m0-storage-bootstrap-schema-baseline.md](2026-03-14-task-m0-storage-bootstrap-schema-baseline.md)

## Кроки

1. Імплементувати шлях ініціалізації async engine для bootstrap storage.
2. Додати probe з'єднання, який швидко завершується помилкою, коли Postgres недосяжний.
3. Додати виконання або валідацію migration у той самий шлях startup.
4. Експортувати результати readiness storage і окремі типи помилок для споживання шарами bootstrap і health.

## Ризики

- Startup стане крихким, якщо помилки з'єднання і migration відображатимуться через один непрозорий шлях помилки.
- Тимчасова bootstrap-логіка тут пізніше конфліктуватиме з канонічною сторі runtime bootstrap.

## Критерії приймання

- Один startup hook storage перевіряє і з'єднання з database, і readiness schema.
- Помилки з'єднання і помилки migration відображаються як окремі operator-facing помилки.
- Readiness contract достатньо вузький для повторного використання в bootstrap і health без дублювання перевірок storage.
- Задача не перевизначає ширші питання життєвого циклу runtime поза readiness storage.

## Посилання

- Батьківський епік: [M0: готовність основ](2026-03-14-epic-m0-foundations-ready.md)
- Батьківська сторі: [M0: ініціалізація сховища](2026-03-14-story-m0-storage-bootstrap.md)
- Залежить від задачі: [2026-03-14-task-m0-storage-bootstrap-storage-surface-alembic.md](2026-03-14-task-m0-storage-bootstrap-storage-surface-alembic.md)
- Залежить від задачі: [2026-03-14-task-m0-storage-bootstrap-schema-baseline.md](2026-03-14-task-m0-storage-bootstrap-schema-baseline.md)
- Батьківський план: [2026-03-14-mvp-delivery-plan.md](2026-03-14-mvp-delivery-plan.md)
- Специфікація архітектури: [architecture-spec.md](../../project/architecture-spec.md)
