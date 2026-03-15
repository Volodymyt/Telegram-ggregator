# M0: контракт runtime і пакета

Planning ID: 0002
Status: Draft
Last updated: 2026-03-15

## Мета

Зафіксувати канонічний контракт runtime і packaging під `src/telegram_aggregator/`, щоб уся подальша реалізація спиралася на одну стабільну базову лінію import, startup, dependency і unit-test execution.

## Обсяг

- Зробити `src/telegram_aggregator/` єдиним підтримуваним коренем runtime package для MVP.
- Прибрати `src/Telegram-aggregator/` з execution contract, який використовують локальні та Docker startup paths.
- Визначити канонічні service- і login-entry modules, очікувані runtime MVP.
- Узгодити Docker і локальний виклик навколо одного module path і bootstrap contract.
- Визначити відтворювану базову лінію dependencies для runtime, migrations, завантаження configuration, health-звітності й test dependencies.
- Визначити один канонічний контракт виконання unit-тестів для канонічного layout пакета.
- Створити package- і module-placeholders, яких вимагає architecture spec, щоб наступні сторі могли реалізовувати конкретні компоненти без перебудови layout пакета.
- Non-goals: реалізація Telegram intake, бізнес-воркерів, деталей storage schema поза importable module boundaries або feature-level логіки.

## Кроки

1. Реалізувати [M0: контракт runtime і пакета: скелет пакета та канонічні entry-модулі](tasks/01_0003_package_skeleton_entrypoints.md), щоб створити канонічне дерево пакета, component placeholders і стабільні service/login entry-модулі під `src/telegram_aggregator/`.
2. Реалізувати [M0: контракт runtime і пакета: базова лінія залежностей](tasks/02_0004_dependency_baseline.md), щоб зафіксувати одну відтворювану surface залежностей для runtime, migrations, config, observability і тестів у M0.
3. Реалізувати [M0: контракт runtime і пакета: контракт виконання unit-тестів](tasks/03_0005_unit_test_execution_contract.md), щоб зафіксувати одну підтримувану команду, контракт discovery і очікування щодо imports для unit-тестів проти канонічного layout пакета.
4. Завершити [M0: контракт runtime і пакета: узгодження execution contract](tasks/04_0006_execution_contract_alignment.md), щоб прибрати legacy package з підтримуваних Docker- і локальних startup paths після того, як канонічний пакет і test surfaces уже зафіксовано.

## Ризики

- Приховані посилання на legacy package name можуть залишитися в runtime assets і зберегти старий execution path.
- Layout пакета може відхилитися від architecture spec, якщо placeholder-модулі додаватимуться довільно, а не за зафіксованою component structure.
- Слабка базова лінія dependencies може тимчасово розблокувати startup, але все одно залишити migrations або тести без відтворюваного середовища.
- Unit-тести можуть формально вважатися підтримуваними, але залишатися операційно неоднозначними, якщо сторі визначить test dependencies без одного канонічного execution contract.
- Bootstrap login може розійтися з bootstrap сервісу, якщо entry-модулі з самого початку не ділитимуть один package contract.

## Критерії приймання

- Репозиторій запускається через `src/telegram_aggregator`, а не через `src/Telegram-aggregator`.
- Docker і локальне виконання використовують однаковий service entrypoint contract.
- Канонічний login entry module існує під `telegram_aggregator` і сумісний із login-flow M0.
- Базова лінія dependencies є явною й відтворюваною для runtime, migrations і тестових залежностей.
- Існує один канонічний repo-tracked контракт виконання unit-тестів для `src/telegram_aggregator/`.
- Структура пакета містить component placeholders, очікувані architecture spec.
- Жоден repo-tracked runtime path більше не залежить від legacy package як підтримуваного execution contract.

## Посилання

- Батьківський епік: [M0: готовність основ](../0001_foundations_ready.md)
- Батьківський план: [План постачання MVP](../../2026-03-14-mvp-delivery-plan.md)
- Специфікація архітектури: [Специфікація архітектури](../../../../project/architecture-spec.md)
