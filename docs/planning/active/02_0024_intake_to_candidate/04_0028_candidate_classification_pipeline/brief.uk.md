# Бриф

## Коротко

Потрібно провести persisted `tg_message` через processing worker до стійких станів `outdated`, `filtered_out` або `candidate`. Для кандидатів треба зберегти метадані класифікації та передати їх у `aggregation_status='queued'`, не заходячи в події чи публікацію.

## Що потрібно зробити

- [ ] Підключити processing worker до канонічної черги та додати startup recovery для persisted `tg_message` зі статусом `pending`.
- [ ] Завантажувати кожен queued або recovered запис із сховища перед класифікацією.
- [ ] Перевіряти правило застарілого повідомлення до будь-якої фільтрації та позначати такі рядки як `outdated`.
- [ ] Обчислювати й зберігати processing-owned `normalized_text` для свіжих рядків перед запуском фільтрації.
- [ ] Зберігати для свіжих рядків результат як `filtered_out` або `candidate` разом із `event_type` та `event_signal` для кандидатів.
- [ ] Переводити candidate-рядки в `aggregation_status='queued'` і не будувати `candidate_signature`, дедуплікацію подій чи шлях публікації.
