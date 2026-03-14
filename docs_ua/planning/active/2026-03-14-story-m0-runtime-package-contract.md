# M0: контракт runtime і пакета

Status: Draft
Owner: Tech Lead
Last updated: 2026-03-14

## Мета

Визначити канонічний контракт runtime і packaging у `src/telegram_aggregator/`, щоб уся подальша імплементація спиралася на єдину стабільну базову лінію import, startup і dependency.

## Обсяг

- Зробити `src/telegram_aggregator/` єдиним підтримуваним коренем runtime-пакета для MVP.
- Прибрати `src/Telegram-aggregator/` з execution contract, який використовують локальний і Docker startup paths.
- Визначити канонічні service- і login-entry modules, очікувані runtime MVP.
- Узгодити Docker і локальний виклик навколо одного module path і bootstrap contract.
- Закласти відтворювану базову лінію dependency для runtime, migrations, завантаження configuration, health-звітності й тестів.
- Створити package- і module-заглушки, потрібні специфікації архітектури, щоб наступні сторі могли імплементувати конкретні компоненти без зміни layout пакета.
- Non-goals: імплементація Telegram intake, бізнес-worker, деталей storage schema поза importable module boundaries або feature-level логіки.

## Кроки

1. Додати канонічну структуру пакета в `src/telegram_aggregator/` зі стабільними entry modules для bootstrap сервісу та bootstrap login.
2. Прибрати застарілий пакет з усіх runtime-facing startup paths, включно з Docker і будь-яким документованим контрактом локального виклику.
3. Визначити мінімальну базову лінію dependency, потрібну для runtime сервісу, migrations, parsing configuration, observability і тестів.
4. Додати importable package-заглушки для layout компонентів, уже зафіксованого в специфікації архітектури.

## Ризики

- Приховані посилання на застарілу назву пакета можуть залишитися в runtime-артефактах і зберегти старий execution path.
- Layout пакета може відхилитися від специфікації архітектури, якщо module-заглушки додаватимуться довільно, а не за зафіксованою структурою компонентів.
- Слабка базова лінія dependency може тимчасово розблокувати startup, але все одно залишити migrations або тести без відтворюваного середовища.
- Bootstrap login може розійтися з bootstrap сервісу, якщо entry modules з самого початку не поділятимуть один package contract.

## Критерії приймання

- Репозиторій запускається через `src/telegram_aggregator/`, а не через `src/Telegram-aggregator/`.
- Docker і локальне виконання використовують однаковий service entrypoint contract.
- Канонічний login entry module існує в `telegram_aggregator` і сумісний із login-flow M0.
- Базова лінія dependency є явною й відтворюваною для runtime, migration і потреб тестування.
- Структура пакета містить component placeholders, очікувані специфікацією архітектури.
- Жоден runtime path, що відстежується в репозиторії, більше не залежить від застарілого пакета як підтримуваного execution contract.

## Посилання

- Батьківський епік: [M0: готовність основ](2026-03-14-epic-m0-foundations-ready.md)
- Батьківський план: [2026-03-14-mvp-delivery-plan.md](2026-03-14-mvp-delivery-plan.md)
- Специфікація архітектури: [architecture-spec.md](../../project/architecture-spec.md)
