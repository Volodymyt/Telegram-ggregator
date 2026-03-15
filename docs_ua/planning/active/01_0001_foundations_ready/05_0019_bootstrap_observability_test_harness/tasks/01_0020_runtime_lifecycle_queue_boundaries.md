# M0: bootstrap, observability і тестовий каркас: життєвий цикл runtime і межі queue

Planning ID: 0020
Status: Ready
Last updated: 2026-03-15

## Мета

Визначити канонічний життєвий цикл runtime у `bootstrap/`, щоб наступні worker, health hooks і runtime integrations підключалися до одного контракту startup, queue і shutdown.

## Обсяг

- Визначити runtime context під контролем bootstrap для settings, спільних queue instances, зареєстрованих runtime components і стану startup.
- Встановити канонічний порядок startup після того, як configuration і storage readiness уже надаються попередніми сторі M0.
- Створити межі processing-, candidate- і publish-queues без під'єднання конкретних бізнес-воркерів.
- Визначити послідовність graceful shutdown і ownership для зареєстрованих runtime components.
- Винести за межі задачі деталі реалізації клієнта Telethon, дизайн payload health endpoint і bootstrap test fixtures.

## Кроки

1. Визначити модулі або типи `bootstrap/`, які володіють runtime context, реєстрацією components і життєвим циклом queues.
2. Створити межі внутрішньопроцесних queues, яких вимагає architecture spec, не вбудовуючи intake, processing, aggregation або publish-логіку.
3. Реалізувати канонічну orchestration startup, яка споживає провалідовані settings і storage readiness до реєстрації runtime components.
4. Реалізувати послідовність graceful shutdown, щоб зареєстровані runtime components зупинялися чисто й передбачувано.

## Ризики

- Runtime context може перетворитися на контейнер для всього підряд, якщо ownership queues, реєстрації components і стану життєвого циклу не буде явним.
- Створення queues може випадково зафіксувати пізніші бізнес-припущення, якщо межі не залишаться загальними на рівні M0.

## Критерії приймання

- Один канонічний bootstrap entrypoint володіє створенням runtime context, queues і межами реєстрації worker.
- Порядок startup визначено достатньо явно, щоб наступні сторі могли під'єднувати конкретні runtime components без зміни ownership життєвого циклу.
- Порядок graceful shutdown визначений достатньо чітко, щоб наступні runtime components могли чисто зупинятися без перевизначення bootstrap contract.
- У цій задачі не реалізується конкретна поведінка worker для intake, processing, candidate aggregation або publish.

## Посилання

- Батьківський епік: [M0: готовність основ](../../0001_foundations_ready.md)
- Батьківська сторі: [M0: bootstrap, observability і тестовий каркас](../0019_bootstrap_observability_test_harness.md)
- Батьківський план: [План постачання MVP](../../../2026-03-14-mvp-delivery-plan.md)
- Специфікація архітектури: [Специфікація архітектури](../../../../../project/architecture-spec.md)
- Залежить від сторі: [M0: контракт конфігурації та login](../../02_0007_config_login_contract/0007_config_login_contract.md)
- Залежить від сторі: [M0: контракт storage і readiness](../../04_0015_storage_contract_readiness/0015_storage_contract_readiness.md)
