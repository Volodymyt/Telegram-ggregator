# M0: контракт runtime і пакета: скелет пакета та канонічні entry-модулі

Planning ID: 0003
Status: Ready
Last updated: 2026-03-15

## Мета

Зафіксувати канонічне дерево пакета й контракт entry-модулів під `src/telegram_aggregator/`, щоб наступні сторі M0 могли додавати config, storage і bootstrap-поведінку без зміни imports або startup paths.

## Обсяг

- Створити канонічний корінь пакета `src/telegram_aggregator/` і component package placeholders, яких вимагає architecture spec.
- Додати стабільні service- і login-entry modules, що маршрутизують у канонічний bootstrap package contract.
- Визначити мінімальні bootstrap-module placeholders, потрібні для того, щоб entry-модулі імпортувалися через одну стабільну runtime surface.
- Розглядати `src/Telegram-aggregator/` як legacy scaffolding і не додавати нову реалізацію під цим шляхом.
- Винести за межі задачі валідацію config, обробку Telegram session, readiness storage, поведінку життєвого циклу worker і health-звітність.

## Кроки

1. Створити importable package skeleton під `src/telegram_aggregator/` з component directories, уже зафіксованими в architecture spec.
2. Додати `__main__.py` як канонічний service entry module і `login.py` як канонічний login entry module.
3. Спрямувати обидва entry-модулі через стабільні bootstrap-facing module boundaries, а не вбудовувати майбутню runtime-логіку безпосередньо у top-level package files.
4. Тримати package placeholders тонкими й importable, щоб наступні сторі могли наповнювати їх без перейменування модулів або переміщення директорій.

## Ризики

- Довільне іменування placeholders тут змусить наступні сторі знову відкривати канонічний package contract.
- Вбудовування runtime-поведінки безпосередньо в entry-модулі ускладнить подальше чисте розширення робіт над config і bootstrap.
- Неявний розподіл відповідальності між `__main__.py`, `login.py` і `bootstrap/` може призвести до розходження service- і login-flows до того, як runtime contract стабілізується.

## Критерії приймання

- `src/telegram_aggregator/` існує як єдиний підтримуваний корінь runtime package для MVP.
- Component package placeholders з architecture spec наявні й importable під канонічним пакетом.
- `python -m telegram_aggregator` і `python -m telegram_aggregator.login` резолвляться через канонічні entry-модулі під `telegram_aggregator`.
- Під `src/Telegram-aggregator/` не додається нова поверхня реалізації.

## Посилання

- Батьківський епік: [M0: готовність основ](../../0001_foundations_ready.md)
- Батьківська сторі: [M0: контракт runtime і пакета](../0002_runtime_package_contract.md)
- Батьківський план: [План постачання MVP](../../../2026-03-14-mvp-delivery-plan.md)
- Специфікація архітектури: [Специфікація архітектури](../../../../../project/architecture-spec.md)
