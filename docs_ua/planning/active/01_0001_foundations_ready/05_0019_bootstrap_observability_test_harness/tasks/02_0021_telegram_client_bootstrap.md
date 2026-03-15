# M0: bootstrap, observability і тестовий каркас: bootstrap клієнта Telegram і readiness сесії

Planning ID: 0021
Status: Ready
Last updated: 2026-03-15

## Мета

Додати мінімальний шлях bootstrap клієнта Telegram, щоб звичайний startup міг перевіряти або відкривати налаштовану session і експонувати вузький readiness signal без введення reader behavior.

## Обсяг

- Визначити bootstrap-facing boundary клієнта Telethon, яка повторно використовує канонічний contract session і login із config-робіт M0.
- Інтегрувати startup клієнта Telegram у канонічний runtime lifecycle, визначений bootstrap-story.
- Додати ownership shutdown для клієнта Telegram у тому самому runtime lifecycle.
- Експонувати high-level readiness signal bootstrap клієнта Telegram для споживання health і observability.
- Винести за межі задачі subscriptions на джерела, message handlers і intake behavior.

## Кроки

1. Визначити bootstrap-facing boundary factory або adapter для клієнта, яка повторно використовує канонічний contract session і login.
2. Інтегрувати звичайний startup з перевіркою наявної сесії та окремими operator-facing failures для відсутнього або непридатного session state.
3. Інтегрувати shutdown клієнта Telegram у канонічний runtime lifecycle.
4. Експонувати вузький readiness signal bootstrap Telegram для наступних layers health і observability.

## Ризики

- Startup Telegram може розійтися з канонічним login path, якщо тут повторно реалізувати валідацію session і семантику operator-facing failures.
- Надто широка модель readiness тут може створити враження успішної subscription на sources або startup reader до того, як ці контракти взагалі з'являться.

## Критерії приймання

- Звичайний startup повторно використовує канонічний contract session і login та окремо показує збої відсутньої або непридатної session.
- Старт і зупинка клієнта Telegram інтегровані в канонічний життєвий цикл bootstrap без під'єднання reader behavior.
- Існує вузький readiness signal bootstrap клієнта Telegram для повторного використання в health і observability.
- Ця задача не реєструє subscriptions на sources і не реалізує логіку Telegram intake.

## Посилання

- Батьківський епік: [M0: готовність основ](../../0001_foundations_ready.md)
- Батьківська сторі: [M0: bootstrap, observability і тестовий каркас](../0019_bootstrap_observability_test_harness.md)
- Батьківський план: [План постачання MVP](../../../2026-03-14-mvp-delivery-plan.md)
- Вимоги: [Вимоги](../../../../../project/requirements.md)
- Специфікація архітектури: [Специфікація архітектури](../../../../../project/architecture-spec.md)
- Залежить від сторі: [M0: контракт конфігурації та login](../../02_0007_config_login_contract/0007_config_login_contract.md)
- Залежить від задачі: [01_0020_runtime_lifecycle_queue_boundaries.md](01_0020_runtime_lifecycle_queue_boundaries.md)
