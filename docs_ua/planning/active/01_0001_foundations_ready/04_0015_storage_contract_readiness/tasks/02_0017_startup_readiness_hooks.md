# M0: контракт storage і readiness: readiness startup і migration hooks

Planning ID: 0017
Status: Ready
Last updated: 2026-03-15

## Мета

Надати один шлях ініціалізації storage, який доводить досяжність Postgres і health migrations до початку роботи runtime workers.

## Обсяг

- Реалізувати ініціалізацію storage, яка відкриває async engine, перевіряє database connectivity і виконує або перевіряє migrations на startup.
- Відрізняти operator-facing failures для досяжності database і виконання migrations.
- Експонувати вузький readiness contract, який можуть споживати bootstrap і health layers.
- Винести за межі задачі загальне керування життєвим циклом worker і реалізацію health endpoint, що належать bootstrap story.

## Кроки

1. Реалізувати шлях ініціалізації async engine для канонічного storage readiness.
2. Додати connectivity probe, який швидко завершується помилкою, коли Postgres недосяжний.
3. Додати виконання або валідацію migrations у той самий startup path.
4. Експонувати результати readiness storage і окремі failure types для споживання bootstrap- і health-layers.

## Ризики

- Startup стане крихким, якщо збої connectivity і migrations показуватимуться через один непрозорий шлях помилки.
- Тимчасова bootstrap-логіка тут пізніше конфліктуватиме з канонічною story runtime bootstrap.

## Критерії приймання

- Один startup hook storage перевіряє і database connectivity, і schema readiness.
- Connectivity failures і migration failures відображаються як окремі operator-facing помилки.
- Readiness contract є достатньо вузьким для повторного використання bootstrap і health без дублювання storage checks.
- Задача не реалізує ширші concerns життєвого циклу runtime поза readiness storage.

## Посилання

- Батьківський епік: [M0: готовність основ](../../0001_foundations_ready.md)
- Батьківська сторі: [M0: контракт storage і readiness](../0015_storage_contract_readiness.md)
- Батьківський план: [План постачання MVP](../../../2026-03-14-mvp-delivery-plan.md)
- Специфікація архітектури: [Специфікація архітектури](../../../../../project/architecture-spec.md)
- Залежить від задачі: [01_0013_storage_surface_alembic.md](../../03_0012_storage_foundation/tasks/01_0013_storage_surface_alembic.md)
- Залежить від задачі: [02_0014_schema_baseline.md](../../03_0012_storage_foundation/tasks/02_0014_schema_baseline.md)
