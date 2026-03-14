# M0: bootstrap, observability і тестовий каркас

Status: Draft
Owner: Tech Lead
Last updated: 2026-03-14

## Мета

Зробити канонічний пакет таким, що запускається, спостерігається і тестується, щоб наступні зрізи могли додавати runtime-поведінку без вигадування lifecycle, health чи verification scaffolding посеред роботи.

## Обсяг

- Визначити послідовність bootstrap сервісу та поведінку graceful shutdown для канонічного пакета.
- Створити межі queue і реєстрації worker, які наступні сторі заповнять конкретною логікою intake, processing, aggregation і publish.
- Зробити структуроване JSON logging типовим форматом runtime.
- Додати легкий HTTP health endpoint із семантикою readiness для Telegram, Postgres і liveness worker на високому рівні.
- Закласти початковий test harness для канонічного layout пакета, включно з bootstrap-орієнтованими тестами та fixtures.
- Non-goals: імплементація логіки Telegram intake, бізнес-логіки worker, повних integration suites або перевірок місткості й latency.

## Кроки

1. Визначити канонічний порядок startup для settings, storage, runtime queue, readiness login/session, реєстрації worker і health-звітності.
2. Додати graceful shutdown, щоб runtime-компоненти зупинялися чисто й залишали чіткі operator-visible logs.
3. Зафіксувати контракт структурованого logging і легкий health endpoint, який показує readiness без обіцянки глибокої діагностики.
4. Створити базовий test harness для канонічного пакета, щоб bootstrap, validation і health-поведінку можна було перевіряти в automated tests.

## Ризики

- Порядок bootstrap може стати нестабільним, якщо readiness checks і реєстрація worker будуть переплетені без чіткого lifecycle contract.
- Health-звітність може створювати хибне відчуття надійності, якщо вона не розрізнятиме успіх конфігурації, readiness Telegram, readiness database і liveness worker.
- Logging може стати непослідовним, якщо структурований output не буде визначено до того, як наступні сторі почнуть emitting runtime events.
- Test scaffolding може бути надто поверхневим для захисту рефакторингів, якщо він рано не заякорить канонічний пакет і bootstrap entrypoint.

## Критерії приймання

- Сервіс чисто запускається і зупиняється через канонічний шлях bootstrap пакета.
- Межі створення queue і реєстрації worker визначені достатньо явно, щоб наступні сторі могли під'єднати конкретні worker без зміни структури bootstrap.
- Структуровані JSON logs є форматом runtime за замовчуванням.
- Легкий health endpoint показує readiness для Telegram, Postgres і liveness worker на високому рівні.
- Automated tests можна запускати проти канонічного layout пакета, і вони покривають bootstrap-орієнтовану поведінку.

## Посилання

- Батьківський епік: [M0: готовність основ](2026-03-14-epic-m0-foundations-ready.md)
- Батьківський план: [2026-03-14-mvp-delivery-plan.md](2026-03-14-mvp-delivery-plan.md)
- Вимоги: [requirements.md](../../project/requirements.md)
- Специфікація архітектури: [architecture-spec.md](../../project/architecture-spec.md)
