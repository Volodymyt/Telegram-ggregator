# M0: контракт storage і readiness

Planning ID: 0015
Status: Draft
Last updated: 2026-03-15

## Мета

Надати один стабільний storage contract для repositories, startup readiness і storage verification, щоб runtime bootstrap і наступні feature-зрізи могли будуватися на довговічній persistence-поведінці без перепроєктування storage layer.

## Обсяг

- Визначити межу repository layer для persistence повідомлень і подій поверх канонічного storage package і базової schema.
- Реалізувати мінімальні persistence primitives, потрібні для наступних story reader, processing, aggregation і publish.
- Додати один storage readiness path, який відрізняє досяжність database від health migrations.
- Захистити storage contract сфокусованою automated verification для repositories, migrations і readiness behavior.
- Non-goals: перевизначення полів базової schema, переробка surface storage package або поглинання ширших concerns життєвого циклу runtime і health endpoint.

## Кроки

1. Реалізувати [M0: контракт storage і readiness: межа repository і примітиви збереження](tasks/01_0016_repository_boundary.md), щоб визначити мінімальний стабільний repository contract поверх базової schema.
2. Реалізувати [M0: контракт storage і readiness: readiness startup і migration hooks](tasks/02_0017_startup_readiness_hooks.md), щоб додати один шлях ініціалізації storage, який доводить досяжність database і health migrations до старту worker.
3. Завершити [M0: контракт storage і readiness: покриття верифікації](tasks/03_0018_verification_coverage.md), щоб захистити migrations, readiness і базові persistence primitives автоматизованим покриттям.

## Ризики

- Межі repository можуть стати надто широкими, якщо ця сторі почне кодувати наступні бізнес-workflows замість самого storage contract.
- Startup залишатиметься крихким, якщо readiness і далі показуватиме збої connectivity та migration через один непрозорий шлях помилки.
- Verification storage може незграбно перетинатися з ширшими bootstrap-тестами, якщо ця сторі не триматиме фокус на storage-specific acceptance signals.

## Критерії приймання

- Існує межа repository для persistence повідомлень і подій, на якій наступні сторі можуть будуватися без перепроєктування storage layer.
- Перші persistence primitives можуть створювати, читати й оновлювати базові records, включно з ідемпотентним persistence повідомлень із джерел за `(source_chat_id, source_message_id)`.
- Один readiness hook storage перевіряє і database connectivity, і schema readiness, повертаючи окремі operator-facing failures.
- Automated verification покриває базовий шлях migrations, behavior storage readiness і перші primitives repository, не розширюючись у не-storage workflows.

## Посилання

- Батьківський епік: [M0: готовність основ](../0001_foundations_ready.md)
- Батьківський план: [План постачання MVP](../../2026-03-14-mvp-delivery-plan.md)
- Вимоги: [Вимоги](../../../../project/requirements.md)
- Специфікація архітектури: [Специфікація архітектури](../../../../project/architecture-spec.md)
- Залежить від сторі: [M0: контракт runtime і пакета](../01_0002_runtime_package_contract/0002_runtime_package_contract.md)
- Залежить від сторі: [M0: контракт конфігурації та login](../02_0007_config_login_contract/0007_config_login_contract.md)
- Залежить від сторі: [M0: foundation для storage](../03_0012_storage_foundation/0012_storage_foundation.md)
- Downstream reference: [M0: bootstrap, observability і тестовий каркас](../05_0019_bootstrap_observability_test_harness/0019_bootstrap_observability_test_harness.md) має споживати readiness hook storage із цієї сторі замість повторної реалізації database checks.
