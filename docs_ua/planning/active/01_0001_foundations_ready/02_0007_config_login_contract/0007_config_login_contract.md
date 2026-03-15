# M0: контракт конфігурації та login

Planning ID: 0007
Status: Draft
Last updated: 2026-03-15

## Мета

Зафіксувати операторський контракт startup так, щоб configuration, validation і поведінка login швидко завершувалися помилкою та залишалися узгодженими між локальним виконанням і виконанням у контейнері.

## Обсяг

- Визначити контракт environment variables для startup, включно з Telegram credentials, session path, database URL, target channel, config path, `LOG_LEVEL`, `DRY_RUN` і `LOGIN`.
- Визначити YAML-контракт для sources, filters, repost settings і runtime settings, пов'язаних із queue, які потрібні на етапі startup.
- Валідувати підтримувані source identifier як `@username`, `t.me/...` або числові identifier там, де це підтримується, а target identifier як username або числовий identifier.
- Валідувати релевантні для startup filter- і runtime-семантики, включно з `mode`, `case_insensitive`, перемикачами normalization і розмірами queue.
- Забезпечити документоване правило режиму `all`, за яким усі include-rules мають спільні `event_type` і `event_signal`.
- Узгодити `python -m telegram_aggregator.login` і `LOGIN=1` навколо одного session-bootstrap contract і одного правила обробки session path.
- Визначити дієву operator-facing семантику помилок для невалідного env, невалідного YAML, непідтримуваних форматів identifier і непридатних session paths.
- Non-goals: реалізація бізнес-логіки filtering, обробки Telegram events або publication-поведінки поза контрактом startup і login.

## Кроки

1. Реалізувати [M0: контракт конфігурації та login: межа startup settings і env-контракт](tasks/01_0008_startup_settings_boundary.md), щоб завантажувати operator-facing env surface і `CONFIG_PATH` один раз до продовження runtime bootstrap.
2. Продовжити [M0: контракт конфігурації та login: YAML-моделі контракту та завантаження файла](tasks/02_0009_yaml_contract_models.md), щоб зафіксувати типізовану файлову форму конфігурації для sources, filters, repost settings і startup-relevant runtime sections.
3. Додати [M0: контракт конфігурації та login: семантична валідація startup і правила identifier](tasks/03_0010_startup_semantic_validation.md), щоб відхиляти непідтримувані identifier, неузгоджену семантику filters і невалідні startup toggles із дієвими помилками.
4. Завершити [M0: контракт конфігурації та login: спільний session bootstrap і узгодження login](tasks/04_0011_login_session_bootstrap.md), щоб спрямувати `python -m telegram_aggregator.login` і `LOGIN=1` через один session-path contract і один контракт операторських помилок.

## Ризики

- Розподіл validation між кількома модулями може призвести до розходження між документованими правилами configuration і фактичною поведінкою startup.
- Parsing identifier може стати непослідовним між обробкою source, target і login-flows, якщо не буде визначено один спільний шлях validation.
- Команда login і шлях `LOGIN=1` можуть розійтися в поведінці, якщо вони не поділятимуть одну логіку session bootstrap.
- Слабкі startup-помилки можуть ускладнити діагностику операторських збоїв, особливо коли проблеми env і YAML виникають разом.

## Критерії приймання

- Невалідний env або YAML input зупиняє startup до того, як сервіс увійде в steady-state bootstrap.
- Валідація source і target identifier підтримує документовані формати input і відхиляє непідтримувані значення з дієвими помилками.
- Валідація покриває `LOG_LEVEL`, `DRY_RUN`, розміри queue, перемикачі normalization, режим filter і узгодженість режиму `all` для typed include-rules.
- `python -m telegram_aggregator.login` створює або перевіряє session path і використовує ті самі session rules, що й `LOGIN=1`.
- Збої session path, форми config і форматів identifier відображаються достатньо відокремлено, щоб оператор міг виправити їх без аналізу коду.

## Посилання

- Батьківський епік: [M0: готовність основ](../0001_foundations_ready.md)
- Батьківський план: [План постачання MVP](../../2026-03-14-mvp-delivery-plan.md)
- Вимоги: [Вимоги](../../../../project/requirements.md)
- Специфікація архітектури: [Специфікація архітектури](../../../../project/architecture-spec.md)
