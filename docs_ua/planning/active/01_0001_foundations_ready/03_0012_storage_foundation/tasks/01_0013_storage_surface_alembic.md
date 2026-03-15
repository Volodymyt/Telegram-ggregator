# M0: foundation для storage: surface storage і каркас Alembic

Planning ID: 0013
Status: Ready
Last updated: 2026-03-15

## Мета

Зафіксувати один канонічний storage entrypoint для MVP, щоб schema, repositories і bootstrap-логіка будувалися на одній surface інтеграції PostgreSQL і Alembic.

## Обсяг

- Додати skeleton пакета `src/telegram_aggregator/storage/` для створення engine, реєстрації metadata, виконання migrations і storage-specific error types.
- Додати файли проєкту Alembic, потрібні канонічному layout пакета.
- Під'єднати Alembic до SQLAlchemy Core metadata, якою володіє storage package.
- Повторно використовувати контракти runtime і config M0 для wiring залежностей і доступу до `DATABASE_URL`, а не створювати паралельний шлях settings.
- Винести за межі задачі дизайн полів schema, поведінку repository і повне wiring runtime bootstrap.

## Кроки

1. Створити структуру пакета `storage/` і визначити канонічні модулі для створення engine, експонування metadata, migrations і storage errors.
2. Додати конфігураційні файли Alembic у корінь репозиторію й спрямувати їх на канонічну storage metadata.
3. Переконатися, що storage package споживає вже наявну config boundary M0 для `DATABASE_URL`.
4. Задокументувати import- і execution contract, який наступні storage-задачі повинні повторно використовувати.

## Ризики

- Alembic може розійтися з runtime-конфігурацією storage, якщо отримуватиме database settings через окремий path.
- Довільне найменування модулів тут змусить наступні storage-задачі перебудовувати межу пакета.

## Критерії приймання

- `src/telegram_aggregator/storage/` існує як канонічний surface storage package.
- Alembic присутній у репозиторії і резолвить канонічну SQLAlchemy Core metadata без довільного wiring.
- Ініціалізація storage залежить від спільного config contract M0 для database settings.
- Поза канонічним пакетом не вводиться другий шлях ініціалізації storage.

## Посилання

- Батьківський епік: [M0: готовність основ](../../0001_foundations_ready.md)
- Батьківська сторі: [M0: foundation для storage](../0012_storage_foundation.md)
- Батьківський план: [План постачання MVP](../../../2026-03-14-mvp-delivery-plan.md)
- Специфікація архітектури: [Специфікація архітектури](../../../../../project/architecture-spec.md)
- Залежить від сторі: [M0: контракт runtime і пакета](../../01_0002_runtime_package_contract/0002_runtime_package_contract.md)
- Залежить від сторі: [M0: контракт конфігурації та login](../../02_0007_config_login_contract/0007_config_login_contract.md)
