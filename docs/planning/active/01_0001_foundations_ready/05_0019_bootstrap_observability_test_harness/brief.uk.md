# Бриф

## Коротко

Потрібно зробити canonical package придатним до запуску, спостереження та базової перевірки. Це має зафіксувати lifecycle, Telegram bootstrap, health-сервер і каркас тестів для подальших історій.

## Що потрібно зробити

- [ ] Визначити послідовність старту, graceful shutdown і межі черги та реєстрації воркерів у `bootstrap/`.
- [ ] Додати мінімальний Telegram client bootstrap і інтеграцію readiness для session/login під час нормального старту.
- [ ] Налаштувати структуроване JSON-логування як формат runtime за замовчуванням.
- [ ] Реалізувати легкий HTTP health endpoint із readiness для Telegram bootstrap, Postgres і високорівневої liveness воркерів.
- [ ] Побудувати bootstrap-oriented test harness для canonical package layout без дублювання storage-specific перевірок.
