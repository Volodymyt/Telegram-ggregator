# M0: контракт runtime і пакета: узгодження execution contract

Planning ID: 0006
Status: Ready
Last updated: 2026-03-15

## Мета

Прибрати legacy package з підтримуваного execution contract, щоб і Docker, і локальний startup рекламували й споживали один канонічний runtime path.

## Обсяг

- Оновити repo-tracked Docker- і локальні startup assets так, щоб вони викликали канонічний service entrypoint під `telegram_aggregator`.
- Прибрати `src/Telegram-aggregator/` з підтримуваної startup-документації й runtime-facing прикладів команд.
- Визначити, чи legacy package тимчасово лишається як непідтримуваний shim, чи видаляється повністю, але в будь-якому разі залишити його поза підтримуваним MVP contract.
- Тримати service- і login-module paths узгодженими зі скелетом пакета, визначеним runtime contract.
- Винести за межі задачі повну реалізацію bootstrap, поведінку login/session і глибші operability-настанови поза підтримуваним invocation contract.

## Кроки

1. Проаудитити repo-tracked runtime assets і docs, які досі посилаються на `Telegram-aggregator` як на підтримуваний execution path.
2. Оновити Docker і задокументовані локальні startup paths на використання `python -m telegram_aggregator`.
3. Прибрати або чітко знизити статус legacy package в підтримуваному контракті без створення другого канонічного path.
4. Переконатися, що наступні сторі M0 можуть посилатися на один підтримуваний module path для runtime startup.

## Ризики

- Приховані legacy-посилання в Docker або run instructions можуть зберегти старий execution contract навіть після появи канонічного пакета.
- Підтримка обох назв пакетів на рівні документації створить зайву плутанину для операторів під час M0.
- Надто агресивне очищення legacy path може зламати непідтримувані локальні звички, якщо підтримуваний контракт не буде чітко задокументовано заздалегідь.

## Критерії приймання

- Жоден підтримуваний repo-tracked Docker- або локальний startup path більше не використовує `python -m Telegram-aggregator`.
- Docker і документація для локального runtime вказують на один і той самий канонічний service module path.
- Legacy package, якщо він усе ще присутній, більше не описується як підтримуваний MVP execution path.
- Канонічний login path лишається `python -m telegram_aggregator.login` і не перевизначається деінде.

## Посилання

- Батьківський епік: [M0: готовність основ](../../0001_foundations_ready.md)
- Батьківська сторі: [M0: контракт runtime і пакета](../0002_runtime_package_contract.md)
- Батьківський план: [План постачання MVP](../../../2026-03-14-mvp-delivery-plan.md)
- Специфікація архітектури: [Специфікація архітектури](../../../../../project/architecture-spec.md)
- Залежить від задачі: [01_0003_package_skeleton_entrypoints.md](01_0003_package_skeleton_entrypoints.md)
