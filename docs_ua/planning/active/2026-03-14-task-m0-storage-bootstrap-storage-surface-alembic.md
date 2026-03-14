# M0: ініціалізація сховища: поверхня сховища та каркас Alembic

Status: Ready
Owner: TBD
Last updated: 2026-03-14

## Мета

Зафіксувати єдиний канонічний entrypoint storage для MVP, щоб schema, repositories і bootstrap-логіка будувалися на одній і тій самій поверхні інтеграції PostgreSQL та Alembic.

## Обсяг

- Додати скелет пакета `src/telegram_aggregator/storage/` для створення engine, реєстрації metadata, виконання migration і storage-specific error types.
- Додати файли проєкту Alembic, потрібні канонічному layout пакета.
- Підключити Alembic до metadata SQLAlchemy Core, якою володіє storage package.
- Повторно використати контракти runtime і config M0 для wiring dependency й доступу до `DATABASE_URL` замість створення паралельного шляху settings.
- Винести за межі задачі дизайн полів schema, поведінку repository і повне wiring runtime bootstrap.

## Залежності

- [2026-03-14-story-m0-runtime-package-contract.md](2026-03-14-story-m0-runtime-package-contract.md)
- [2026-03-14-story-m0-config-login-contract.md](2026-03-14-story-m0-config-login-contract.md)

## Кроки

1. Створити структуру пакета `storage/` і визначити канонічні modules для створення engine, exposure metadata, migrations і storage errors.
2. Додати конфігураційні файли Alembic у корінь репозиторію й спрямувати їх на канонічну metadata storage.
3. Переконатися, що storage package споживає наявну межу config M0 для `DATABASE_URL`.
4. Задокументувати контракт import і execution, який повинні повторно використовувати наступні storage-задачі.

## Ризики

- Alembic може відхилитися від runtime-конфігурації storage, якщо він діставатиме database settings окремим шляхом.
- Довільне іменування modules тут змусить наступні storage-задачі змінювати межу пакета.

## Критерії приймання

- `src/telegram_aggregator/storage/` існує як канонічна поверхня storage package.
- Alembic присутній у репозиторії й використовує канонічну metadata SQLAlchemy Core без довільного wiring.
- Ініціалізація storage залежить від спільного контракту config M0 для database settings.
- Поза канонічним пакетом не з'являється другий шлях bootstrap storage.

## Посилання

- Батьківський епік: [M0: готовність основ](2026-03-14-epic-m0-foundations-ready.md)
- Батьківська сторі: [M0: ініціалізація сховища](2026-03-14-story-m0-storage-bootstrap.md)
- Батьківський план: [2026-03-14-mvp-delivery-plan.md](2026-03-14-mvp-delivery-plan.md)
- Специфікація архітектури: [architecture-spec.md](../../project/architecture-spec.md)
