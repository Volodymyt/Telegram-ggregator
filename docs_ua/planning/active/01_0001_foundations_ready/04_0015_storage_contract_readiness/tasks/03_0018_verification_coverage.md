# M0: контракт storage і readiness: покриття верифікації

Planning ID: 0018
Status: Ready
Last updated: 2026-03-15

## Мета

Захистити storage contract і readiness behavior автоматизованою верифікацією, щоб наступні роботи M0 і M1 не ламали migrations, readiness checks або базову persistence-поведінку.

## Обсяг

- Додати automated verification для базової ревізії Alembic.
- Перевірити перші primitives repository поверх канонічної schema, включно з ідемпотентним persistence повідомлень із джерел.
- Перевірити, що ініціалізація storage відрізняє connectivity failures від migration failures.
- Винести за межі задачі тести наступних бізнес-workflows для candidate recovery, deduplication і publication behavior.

## Кроки

1. Додати smoke-покриття migrations для початкової ревізії Alembic.
2. Додати repository-тести для базових операцій create, fetch, update і ідемпотентного persistence повідомлень із джерел.
3. Додати readiness-тести, які доводять, що ініціалізація storage відрізняє connectivity failures від migration failures.
4. Тримати surface verification обмеженою очікуваннями щодо storage contract і readiness.

## Ризики

- Без automated coverage storage contract буде тихо деградувати, коли наступні віхи додаватимуть runtime-поведінку.
- Scope тестів може стати шумним, якщо почне покривати майбутні candidate- або publish-workflows до того, як їхні контракти взагалі з'являться.

## Критерії приймання

- Automated verification покриває базовий шлях migrations.
- Automated verification покриває перші primitives repository для `message_records` і `event_records`.
- Automated verification доводить, що readiness storage відрізняє connectivity failures від migration failures.
- Scope verification залишається обмеженою storage contract і readiness behavior.

## Посилання

- Батьківський епік: [M0: готовність основ](../../0001_foundations_ready.md)
- Батьківська сторі: [M0: контракт storage і readiness](../0015_storage_contract_readiness.md)
- Батьківський план: [План постачання MVP](../../../2026-03-14-mvp-delivery-plan.md)
- Специфікація архітектури: [Специфікація архітектури](../../../../../project/architecture-spec.md)
- Залежить від задачі: [02_0014_schema_baseline.md](../../03_0012_storage_foundation/tasks/02_0014_schema_baseline.md)
- Залежить від задачі: [01_0016_repository_boundary.md](01_0016_repository_boundary.md)
- Залежить від задачі: [02_0017_startup_readiness_hooks.md](02_0017_startup_readiness_hooks.md)
