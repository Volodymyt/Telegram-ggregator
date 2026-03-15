# M0: контракт конфігурації та login: семантична валідація startup і правила identifier

Planning ID: 0010
Status: Ready
Last updated: 2026-03-15

## Мета

Забезпечити семантичну валідацію startup до ініціалізації runtime, щоб непідтримувані identifier і неузгоджена семантика конфігурації завершувалися дієвими operator-facing помилками.

## Обсяг

- Валідувати підтримувані source identifier як `@username`, `t.me/...` або числові identifier там, де це підтримується, а target identifier як username або числовий identifier.
- Валідувати `LOG_LEVEL`, `DRY_RUN`, розміри queue, значення режимів filter і перемикачі normalization, які використовуються на startup.
- Забезпечити документоване правило режиму `all`, за яким усі typed include-rules мають спільні `event_type` і `event_signal`.
- Повертати окремі operator-facing validation failures для env values, YAML semantics і форматів identifier.
- Винести за межі задачі flow авторизації Telethon і ширший bootstrap runtime workers.

## Кроки

1. Додати спільні primitives validation для підтримуваних форматів source і target identifier.
2. Валідувати startup semantics для log level, booleans, розмірів queue і перемикачів normalization.
3. Забезпечити семантику режимів filter, включно з правилом узгодженості режиму `all` для typed include-rules.
4. Зупиняти startup до ініціалізації runtime при semantic validation failure і зберігати дієвий контекст помилки для операторів.

## Ризики

- Parsing identifier може розійтися між обробкою source і target, якщо тут не буде визначено один спільний шлях validation.
- Відкладення semantic validation до wiring runtime призведе до частково ініціалізованих bootstrap states і складніших для діагностики збоїв.
- Злиття всіх semantic failures в одну непрозору config error послабить operator contract, який ця сторі має зафіксувати.

## Критерії приймання

- Валідація source і target identifier підтримує документовані формати input і відхиляє непідтримувані значення з дієвими помилками.
- Валідація покриває `LOG_LEVEL`, `DRY_RUN`, розміри queue, перемикачі normalization, режим filter і узгодженість режиму `all` для typed include-rules.
- Semantic validation failures зупиняють startup до входу сервісу в runtime initialization.
- Оператори можуть відрізнити збої env-value, YAML-semantic і identifier-format без аналізу коду.

## Посилання

- Батьківський епік: [M0: готовність основ](../../0001_foundations_ready.md)
- Батьківська сторі: [M0: контракт конфігурації та login](../0007_config_login_contract.md)
- Батьківський план: [План постачання MVP](../../../2026-03-14-mvp-delivery-plan.md)
- Вимоги: [Вимоги](../../../../../project/requirements.md)
- Специфікація архітектури: [Специфікація архітектури](../../../../../project/architecture-spec.md)
- Залежить від задачі: [01_0008_startup_settings_boundary.md](01_0008_startup_settings_boundary.md)
- Залежить від задачі: [02_0009_yaml_contract_models.md](02_0009_yaml_contract_models.md)
