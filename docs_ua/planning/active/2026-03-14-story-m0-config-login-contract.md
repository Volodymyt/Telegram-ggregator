# M0: контракт конфігурації та login

Status: Draft
Owner: Tech Lead
Last updated: 2026-03-14

## Мета

Зафіксувати операторський контракт startup так, щоб configuration, validation і поведінка login швидко завершувалися помилкою та залишалися узгодженими між локальним запуском і запуском у контейнері.

## Обсяг

- Визначити контракт environment variables для startup, включно з Telegram credentials, session path, database URL, target channel, config path, `LOG_LEVEL`, `DRY_RUN` і `LOGIN`.
- Визначити YAML-контракт для sources, filters, налаштувань repost і runtime-параметрів queue, потрібних під час startup.
- Валідувати підтримувані source identifier як `@username`, `t.me/...` або числові identifier там, де це підтримується, а target identifier як username або числовий identifier.
- Валідувати релевантні для startup filter- і runtime-семантики, включно з `mode`, `case_insensitive`, перемикачами normalization і розмірами queue.
- Забезпечити документоване правило режиму `all`, за яким усі include-rules мають спільні `event_type` і `event_signal`.
- Узгодити `python -m telegram_aggregator.login` і `LOGIN=1` навколо одного контракту bootstrap session і одного правила обробки session path.
- Визначити дієву operator-facing семантику помилок для невалідного env, невалідного YAML, непідтримуваних форматів identifier і непридатних шляхів session.
- Non-goals: імплементація бізнес-логіки filter, обробки Telegram events або поведінки publication за межами контракту startup і login.

## Кроки

1. Змоделювати межу startup settings так, щоб env і YAML input завантажувалися один раз і валідувалися до продовження bootstrap сервісу.
2. Провалідувати форму YAML для sources, typed include-rules, exclude-rules, repost options і runtime settings, які впливають на семантику startup.
3. Провалідувати формати identifier, значення log level, розміри queue, boolean-перемикачі та правила узгодженості режиму `all` до ініціалізації runtime.
4. Спрямувати обидва підтримувані шляхи login через один session-bootstrap flow з однаковою валідацією session path і однаковою operator-facing поведінкою помилок.

## Ризики

- Розділення validation між кількома модулями може призвести до розходження між задокументованими правилами configuration і фактичною поведінкою startup.
- Parsing identifier може стати непослідовним між обробкою source, target і login-flows, якщо не буде визначено один спільний шлях validation.
- Команда login і шлях `LOGIN=1` можуть розійтися в поведінці, якщо вони не поділятимуть одну й ту саму логіку session-bootstrap.
- Слабкі startup-помилки можуть ускладнити діагностику операторських збоїв, особливо коли проблеми env і YAML виникають разом.

## Критерії приймання

- Невалідний env або YAML input зупиняє startup до входу сервісу в steady-state bootstrap.
- Валідація source і target identifier підтримує документовані формати input і відхиляє непідтримувані значення з дієвими помилками.
- Валідація покриває `LOG_LEVEL`, `DRY_RUN`, розміри queue, перемикачі normalization, режим filter та узгодженість режиму `all` для typed include-rules.
- `python -m telegram_aggregator.login` створює або валідує session path і використовує ті самі правила session, що й `LOGIN=1`.
- Збої session path, форми config і форматів identifier відображаються достатньо відокремлено, щоб оператор міг виправити їх без аналізу коду.

## Посилання

- Батьківський епік: [M0: готовність основ](2026-03-14-epic-m0-foundations-ready.md)
- Батьківський план: [2026-03-14-mvp-delivery-plan.md](2026-03-14-mvp-delivery-plan.md)
- Вимоги: [requirements.md](../../project/requirements.md)
- Специфікація архітектури: [architecture-spec.md](../../project/architecture-spec.md)
