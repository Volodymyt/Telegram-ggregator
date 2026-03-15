# M0: контракт runtime і пакета: базова лінія залежностей

Planning ID: 0004
Status: Ready
Last updated: 2026-03-15

## Мета

Зафіксувати одну відтворювану базову лінію dependencies для M0, щоб runtime, config, storage, observability, migrations і tooling unit-тестів спиралися на одну install surface.

## Обсяг

- Тримати один зафіксований `requirements.txt` як канонічну surface залежностей для локальних і Docker-інсталяцій.
- Визначити мінімальний набір базових бібліотек, уже продиктований architecture spec і активними M0 story.
- Покрити runtime, parsing config, доступ до Postgres, migrations, observability hooks і test dependencies в межах однієї базової лінії.
- Винести за межі задачі канонічну команду запуску unit-тестів, вміст migrations, bootstrap-поведінку, реалізацію health endpoint і будь-який перехід до installable package workflow на кшталт `pyproject.toml`.

## Кроки

1. Визначити мінімальний набір базових бібліотек, який уже випливає з architecture spec і активних M0 story.
2. Зафіксувати їх в одному відтворюваному `requirements.txt`, а не розносити runtime- і test-dependencies між паралельними механізмами.
3. Тримати Docker і локальний setup узгодженими на одному файлі залежностей і однакових очікуваннях щодо встановлення.
4. Задокументувати базову лінію dependencies достатньо чітко, щоб наступні сторі M0 могли повторно її використовувати без повторного відкриття рішень щодо packaging або test dependencies.

## Ризики

- Часткова базова лінія може дозволити пройти startup imports, але залишити migrations або тести без відтворюваного середовища.
- Додавання другого механізму packaging зараз повторно відкриє рішення, яке цій сторі достатньо лише стабілізувати, а не розширювати.
- Перевантаження цієї задачі опціональним tooling створить churn ще до того, як runtime contract стане виконуваним.

## Критерії приймання

- `requirements.txt` є канонічною базовою лінією dependencies M0 для Docker і локального setup.
- Базова лінія є достатньо явною для runtime imports, parsing config, migrations, observability hooks і встановлення або збору test dependencies.
- Наступним сторі M0 не потрібно вводити другий механізм встановлення залежностей, щоб продовжити роботу.
- Задача не додає `pyproject.toml` або інший паралельний packaging contract.

## Посилання

- Батьківський епік: [M0: готовність основ](../../0001_foundations_ready.md)
- Батьківська сторі: [M0: контракт runtime і пакета](../0002_runtime_package_contract.md)
- Батьківський план: [План постачання MVP](../../../2026-03-14-mvp-delivery-plan.md)
- Специфікація архітектури: [Специфікація архітектури](../../../../../project/architecture-spec.md)
- Наступна задача: [03_0005_unit_test_execution_contract.md](03_0005_unit_test_execution_contract.md)
