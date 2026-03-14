# M0: ініціалізація сховища: покриття верифікації

Status: Ready
Owner: TBD
Last updated: 2026-03-14

## Мета

Захистити storage bootstrap contract автоматизованою верифікацією, щоб подальша робота M0 і M1 не ламала migrations, readiness checks або базову поведінку persistence.

## Обсяг

- Додати автоматизовану верифікацію для базової ревізії Alembic.
- Перевірити перші repository primitives на канонічній schema, включно з ідемпотентним збереженням source-message.
- Перевірити, що ініціалізація storage розрізняє помилки з'єднання і помилки migration.
- Винести за межі задачі тести майбутніх бізнес-workflow для recovery candidate, deduplication і publication.

## Залежності

- [2026-03-14-task-m0-storage-bootstrap-schema-baseline.md](2026-03-14-task-m0-storage-bootstrap-schema-baseline.md)
- [2026-03-14-task-m0-storage-bootstrap-repository-boundary.md](2026-03-14-task-m0-storage-bootstrap-repository-boundary.md)
- [2026-03-14-task-m0-storage-bootstrap-startup-readiness-hooks.md](2026-03-14-task-m0-storage-bootstrap-startup-readiness-hooks.md)

## Кроки

1. Додати smoke-покриття migrations для початкової ревізії Alembic.
2. Додати repository tests для базової поведінки create, fetch, update та ідемпотентного збереження source-message.
3. Додати readiness tests, які доводять, що ініціалізація storage розрізняє помилки з'єднання і помилки migration.
4. Зберегти поверхню verification обмеженою очікуваннями bootstrap storage.

## Ризики

- Без automated coverage storage contract тихо деградуватиме, коли наступні milestones додаватимуть runtime-поведінку.
- Scope тестів може стати шумним, якщо він почне покривати майбутні candidate- чи publish-workflows до появи відповідних контрактів.

## Критерії приймання

- Automated verification покриває базовий шлях migration.
- Automated verification покриває перші repository primitives на `message_records` і `event_records`.
- Automated verification доводить, що readiness storage розрізняє помилки з'єднання і помилки migration.
- Scope verification залишається обмеженим поведінкою bootstrap storage.

## Посилання

- Батьківський епік: [M0: готовність основ](2026-03-14-epic-m0-foundations-ready.md)
- Батьківська сторі: [M0: ініціалізація сховища](2026-03-14-story-m0-storage-bootstrap.md)
- Залежить від задачі: [2026-03-14-task-m0-storage-bootstrap-schema-baseline.md](2026-03-14-task-m0-storage-bootstrap-schema-baseline.md)
- Залежить від задачі: [2026-03-14-task-m0-storage-bootstrap-repository-boundary.md](2026-03-14-task-m0-storage-bootstrap-repository-boundary.md)
- Залежить від задачі: [2026-03-14-task-m0-storage-bootstrap-startup-readiness-hooks.md](2026-03-14-task-m0-storage-bootstrap-startup-readiness-hooks.md)
- Батьківський план: [2026-03-14-mvp-delivery-plan.md](2026-03-14-mvp-delivery-plan.md)
- Специфікація архітектури: [architecture-spec.md](../../project/architecture-spec.md)
