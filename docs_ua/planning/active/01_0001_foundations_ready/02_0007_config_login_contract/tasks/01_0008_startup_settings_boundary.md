# M0: контракт конфігурації та login: межа startup settings і env-контракт

Planning ID: 0008
Status: Ready
Last updated: 2026-03-15

## Мета

Визначити одну канонічну межу startup settings, щоб service- і login-flows завантажували operator-provided environment input один раз і завершувалися помилкою до початку wiring runtime.

## Обсяг

- Визначити канонічну surface `src/telegram_aggregator/config/` для startup settings, path resolution і discovery config file.
- Парсити обов'язкові env vars `TG_API_ID`, `TG_API_HASH`, `TG_SESSION_PATH`, `DATABASE_URL`, `TARGET_CHANNEL` і `CONFIG_PATH`.
- Парсити необов'язкові startup toggles `LOG_LEVEL`, `DRY_RUN` і `LOGIN` у ту саму типізовану boundary.
- Валідувати релевантні для startup шляхи достатньо рано, щоб пізніший bootstrap-код не відкривав повторно env parsing або filesystem checks.
- Винести за межі задачі моделювання YAML schema, cross-field семантику filters і поведінку session authorization.

## Кроки

1. Визначити module boundary для завантаження env, розв'язання шляхів і надання startup settings.
2. Парсити обов'язкові й необов'язкові env vars у типізовані startup settings без дублювання логіки в bootstrap entrypoints.
3. Швидко завершуватися помилкою на відсутньому або некоректному env input і непридатних шляхах до config file до продовження runtime bootstrap.
4. Задокументувати спільний контракт startup settings, який наступні задачі M0 повинні повторно використовувати.

## Ризики

- Дубльований env parsing у service- і login-entrypoints повторно відкриє operator contract одразу після його визначення.
- Надто пізня валідація config paths дозволить runtime bootstrap завершуватися менш дієвими помилками, ніж здатен надати config layer.
- Settings object, що вже містить concerns wiring runtime, ускладнить підтримку цілісності наступних робіт над bootstrap.

## Критерії приймання

- Існує один канонічний startup-settings loader для підтримуваної env surface.
- Відсутній або некоректний обов'язковий env input зупиняє startup до входу сервісу в steady-state bootstrap.
- Збої `CONFIG_PATH` відображаються окремо від наступних збоїв YAML shape і semantic validation.
- Наступні сторі M0 можуть споживати спільну boundary startup settings без повторного parsing env input.

## Посилання

- Батьківський епік: [M0: готовність основ](../../0001_foundations_ready.md)
- Батьківська сторі: [M0: контракт конфігурації та login](../0007_config_login_contract.md)
- Батьківський план: [План постачання MVP](../../../2026-03-14-mvp-delivery-plan.md)
- Вимоги: [Вимоги](../../../../../project/requirements.md)
- Специфікація архітектури: [Специфікація архітектури](../../../../../project/architecture-spec.md)
- Залежить від сторі: [M0: контракт runtime і пакета](../../01_0002_runtime_package_contract/0002_runtime_package_contract.md)
