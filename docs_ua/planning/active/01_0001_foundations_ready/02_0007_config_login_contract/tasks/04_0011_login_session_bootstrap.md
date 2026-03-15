# M0: контракт конфігурації та login: спільний session bootstrap і узгодження login

Planning ID: 0011
Status: Ready
Last updated: 2026-03-15

## Мета

Узгодити обидва підтримувані login entry paths на одному session-bootstrap contract, щоб обробка session path і видимі оператору збої лишалися послідовними між локальним і контейнеризованим виконанням.

## Обсяг

- Спрямувати `python -m telegram_aggregator.login` і `LOGIN=1` через один спільний flow bootstrap login/session.
- Повторно використовувати канонічні boundaries startup settings і validation для session-related input замість введення path-specific parsing.
- Визначити одне правило для створення, валідації й відхилення session paths у підтримуваних execution environments.
- Зберегти обробку 2FA інтерактивною й не дозволяти зберігати паролі у відкритому вигляді через env, YAML або конфігурацію під контролем версій.
- Винести за межі задачі обробку Telegram events, reconnect behavior і ширшу orchestration життєвого циклу сервісу.

## Кроки

1. Визначити спільний entry contract для session bootstrap, включно з мінімальними провалідованими settings, яких він потребує.
2. Спрямувати обидва підтримувані login entry paths через одну boundary підготовки session path і авторизації.
3. Відображати session-path failures окремо від authorization failures і загальних config errors.
4. Зберегти звичайний startup із наявним session file, водночас залишивши явний login bootstrap підтримуваним шляхом першої авторизації.

## Ризики

- `LOGIN=1` і `python -m telegram_aggregator.login` швидко розійдуться, якщо збережуть окремі bootstrap code paths.
- Поведінка session path може відрізнятися між локальним і контейнеризованим виконанням, якщо тут не буде зафіксовано правила створення директорій і валідації шляхів.
- Примусова залежність login bootstrap від несуміжної повної service configuration створить зайве operator friction, коли потрібна лише session authorization.

## Критерії приймання

- `python -m telegram_aggregator.login` і `LOGIN=1` використовують один session-bootstrap contract.
- Створення, валідація й обробка збоїв session path відбуваються за однаковим правилом у межах обох підтримуваних login entry paths.
- Збої session path відображаються окремо від authorization failures і загальних config-shape errors.
- Звичайний startup лишається сумісним із наявним session file, а паролі 2FA не зберігаються у відкритому вигляді.

## Посилання

- Батьківський епік: [M0: готовність основ](../../0001_foundations_ready.md)
- Батьківська сторі: [M0: контракт конфігурації та login](../0007_config_login_contract.md)
- Батьківський план: [План постачання MVP](../../../2026-03-14-mvp-delivery-plan.md)
- Вимоги: [Вимоги](../../../../../project/requirements.md)
- Специфікація архітектури: [Специфікація архітектури](../../../../../project/architecture-spec.md)
- Залежить від задачі: [01_0008_startup_settings_boundary.md](01_0008_startup_settings_boundary.md)
- Залежить від задачі: [03_0010_startup_semantic_validation.md](03_0010_startup_semantic_validation.md)
