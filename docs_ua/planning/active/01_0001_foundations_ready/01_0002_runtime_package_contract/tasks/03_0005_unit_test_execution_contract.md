# M0: контракт runtime і пакета: контракт виконання unit-тестів

Planning ID: 0005
Status: Ready
Last updated: 2026-03-15

## Мета

Зафіксувати один канонічний спосіб запуску unit-тестів проти `src/telegram_aggregator/`, щоб наступні сторі M0 могли додавати покриття без повторного відкриття очікувань щодо runner, discovery або import paths.

## Обсяг

- Визначити один підтримуваний unit-test runner і команду для repo-tracked execution проти канонічного layout пакета.
- Визначити мінімальну repo-tracked конфігурацію test runner або документацію, потрібну для стабільного discovery і imports під `src/telegram_aggregator/`.
- Тримати виконання unit-тестів узгодженим із базовою лінією dependencies, уже визначеною для M0.
- Зробити контракт виконання unit-тестів достатньо явним, щоб наступні сторі M0 могли додавати тести без вигадування другого execution path.
- Винести за межі задачі feature-specific test cases, розширення CI pipeline, orchestration integration-тестів і bootstrap- або storage-verification, що належить наступним сторі.

## Кроки

1. Вибрати канонічний unit-test invocation, який працює з канонічним layout пакета й не залежить від legacy package path.
2. Додати мінімальну repo-tracked конфігурацію runner або документацію, потрібну для стабільного discovery і imports.
3. Переконатися, що базова лінія dependencies з задачі `03` є достатньою для підтримуваного unit-test invocation.
4. Задокументувати контракт unit-тестів достатньо чітко, щоб наступні сторі M0 могли додавати покриття без перевизначення runner або семантики команди.

## Ризики

- Неявний unit-test runner змусить наступні сторі вигадувати власні команди й workaround-и для import paths.
- Надто сильне прив'язування контракту unit-тестів до однієї наступної feature story змусить щоразу повторно відкривати runtime contract, коли додається нове покриття.
- Введення кількох підтримуваних test-команд під час M0 розмиє канонічний package contract і створить зайву неоднозначність.

## Критерії приймання

- Існує одна канонічна repo-tracked команда для запуску unit-тестів проти `src/telegram_aggregator/`.
- Підтримуваний unit-test invocation резолвить imports із `telegram_aggregator`, не залежачи від `src/Telegram-aggregator/`.
- Контракт unit-тестів є достатньо явним, щоб наступні сторі M0 могли додавати тести без вибору нового runner чи альтернативного execution path.
- Задача не вводить CI-specific orchestration або другого підтримуваного test runner.

## Посилання

- Батьківський епік: [M0: готовність основ](../../0001_foundations_ready.md)
- Батьківська сторі: [M0: контракт runtime і пакета](../0002_runtime_package_contract.md)
- Батьківський план: [План постачання MVP](../../../2026-03-14-mvp-delivery-plan.md)
- Специфікація архітектури: [Специфікація архітектури](../../../../../project/architecture-spec.md)
- Залежить від задачі: [01_0003_package_skeleton_entrypoints.md](01_0003_package_skeleton_entrypoints.md)
- Залежить від задачі: [02_0004_dependency_baseline.md](02_0004_dependency_baseline.md)
