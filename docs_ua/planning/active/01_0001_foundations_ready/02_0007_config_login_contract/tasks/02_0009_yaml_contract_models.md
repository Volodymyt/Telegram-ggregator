# M0: контракт конфігурації та login: YAML-моделі контракту та завантаження файла

Planning ID: 0009
Status: Ready
Last updated: 2026-03-15

## Мета

Зафіксувати файлову форму конфігурації й шлях parsing так, щоб startup споживав один типізований YAML-контракт для sources, filters, repost options і runtime settings.

## Обсяг

- Визначити типізовані YAML-моделі для `sources`, `filters`, `repost` і `runtime`.
- Парсити файл за `CONFIG_PATH` через один канонічний loading path, який повторно використовує startup validation.
- Валідувати shape-level очікування для typed include-rules, exclude-rules, repost options і startup-relevant runtime settings.
- Тримати secrets і deployment-specific credentials поза YAML-контрактом.
- Винести за межі задачі валідацію форматів identifier, обмеження розмірів queue, узгодженість режиму `all` і session-bootstrap behavior.

## Кроки

1. Визначити типізовані configuration models для задокументованих YAML sections і вкладених rule objects.
2. Завантажувати YAML із розв'язаного `CONFIG_PATH` і мапити збої parsing на operator-facing config errors.
3. Валідувати обов'язкову форму і типи полів для sources, typed include-rules, exclude-rules, repost settings і startup-relevant runtime sections.
4. Експонувати розпарсену файлову конфігурацію через ту саму канонічну config boundary, що й env settings.

## Ризики

- YAML-контракт може розійтися із задокументованими вимогами, якщо shape validation змішати з пізнішими semantic rules у довільних runtime-модулях.
- Дозвіл secrets у YAML підірве зафіксований operator contract, який тримає credentials у змінних середовища.
- Parse errors без прив'язки до полів сповільнять виправлення оператором більше, ніж це потрібно.

## Критерії приймання

- YAML-контракт відповідає задокументованій формі конфігурації для `sources`, `filters`, `repost` і `runtime`.
- Некоректний YAML або shape-level помилки конфігурації зупиняють startup до початку steady-state bootstrap.
- Startup-код споживає один розпарсений file-config object замість повторного parsing YAML у downstream modules.
- Не вводиться друге джерело конфігурації для значень, які вже належать env input.

## Посилання

- Батьківський епік: [M0: готовність основ](../../0001_foundations_ready.md)
- Батьківська сторі: [M0: контракт конфігурації та login](../0007_config_login_contract.md)
- Батьківський план: [План постачання MVP](../../../2026-03-14-mvp-delivery-plan.md)
- Вимоги: [Вимоги](../../../../../project/requirements.md)
- Специфікація архітектури: [Специфікація архітектури](../../../../../project/architecture-spec.md)
- Залежить від задачі: [01_0008_startup_settings_boundary.md](01_0008_startup_settings_boundary.md)
