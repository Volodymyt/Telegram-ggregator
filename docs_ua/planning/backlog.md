# Беклог

Цей документ зберігає пріоритезовану роботу, яка ще не є активною.

## Модель статусів

Для кожного елемента використовуйте один із наведених статусів:

- `Draft`
- `Ready`
- `Blocked`
- `Done`
- `Archived`

## Типи елементів планування

- Канонічні planning-елементи після переведення в [`active/`](active/README.md) і далі використовують ієрархію `epic > story > task`.
- Розділи беклогу на кшталт `M1`, `M2` та подібні заголовки віх є допоміжним групуванням релізів, а не канонічними planning-елементами.
- Записи беклогу описують очікувану майбутню форму роботи й пізніше можуть бути підвищені до канонічних документів epic, story або task.

## Угода щодо назв

- Тримай заголовки елементів беклогу читабельними для людей і без ID, виведених із шляхів.
- Не кодуй у назвах елементів беклогу імена директорій предків, назви файлів або значення `Planning ID`.
- Виражай контекст походження чи залежностей у полі `Links`, якщо це допомагає пріоритизації.

## Шаблон елемента

Використовуйте компактний формат для кожного елемента беклогу:

```md
- [Status] Short title
  - Type: Epic | Story | Task
  - Why it matters:
  - Acceptance signal:
  - Links:
```

## Правило підтримки

- Тримайте список пріоритезованим зверху вниз.
- Записи беклогу мають залишатися гнучкими й не резервують значення `Planning ID`.
- Коли елемент переводиться в [`active/`](active/README.md), признач наступний `Planning ID`, вибери локальний `order` серед сусідів і створи канонічний шлях за угодою найменування активного планування.
- Переміщуйте активні execution plans до [`active/`](active/README.md).
- Переміщуйте завершену або замінену роботу до [`archive/`](archive/README.md).

## Пріоритезовані елементи

Ці елементи навмисно залишаються без канонічних ID і ліній походження шляхів, доки їх не буде підвищено до окремих planning-файлів.

Поточний активний фокус виконання: [M0 Foundations Ready](active/01_0001_foundations_ready/0001_foundations_ready.md).

### M1

- [Draft] M1 Від intake до candidate
  - Type: Epic
  - Why it matters: Забезпечити перший довговічний зріз від Telegram intake до стану candidate без публікації.
  - Acceptance signal: Критерії виходу M1 у плані поставки MVP виконані.
  - Links: [2026-03-14-mvp-delivery-plan.md](active/2026-03-14-mvp-delivery-plan.md)

- [Draft] M1 Intake джерел і дедуплікація повідомлень
  - Type: Story
  - Why it matters: Забезпечити, щоб повідомлення з джерел читалися один раз, зберігалися один раз і безпечно ігнорувалися при повторній доставці.
  - Acceptance signal: Telethon читає налаштовані джерела, одноразово зберігає вхідні повідомлення й виконує дедуплікацію за `(source_chat_id, source_message_id)`.
  - Links: Parent epic: M1 Від intake до candidate; [2026-03-14-mvp-delivery-plan.md](active/2026-03-14-mvp-delivery-plan.md)

- [Draft] M1 Нормалізація та рушій фільтрів
  - Type: Story
  - Why it matters: Зберегти задокументовану семантику match для include- і exclude-rules до того, як почнеться класифікація кандидатів.
  - Acceptance signal: Поведінка filter покриває режими `any` і `all`, а також `case_insensitive` і перемикачі normalization для тексту повідомлень і підписів медіа.
  - Links: Parent epic: M1 Від intake до candidate; [2026-03-14-mvp-delivery-plan.md](active/2026-03-14-mvp-delivery-plan.md)

- [Draft] M1 Конвеєр класифікації кандидатів
  - Type: Story
  - Why it matters: Перетворювати прийняті повідомлення на довговічний стан candidate разом із metadata, потрібними для наступної агрегації подій.
  - Acceptance signal: Обробка через queue зберігає або `filtered_out`, або `candidate` разом із `event_type`, `event_signal` і `candidate_signature`.
  - Links: Parent epic: M1 Від intake до candidate; [2026-03-14-mvp-delivery-plan.md](active/2026-03-14-mvp-delivery-plan.md)

### M2

- [Draft] M2 Зріз публікації події `start`
  - Type: Epic
  - Why it matters: Доставити перший демонстрабельний наскрізний шлях MVP від кандидата `start` до публікації в цільовому каналі.
  - Acceptance signal: Критерії виходу M2 у плані поставки MVP виконані.
  - Links: [2026-03-14-mvp-delivery-plan.md](active/2026-03-14-mvp-delivery-plan.md)

- [Draft] M2 Відкриття події `start`
  - Type: Story
  - Why it matters: Ввести канонічне правило відкриття події, яке визначає, яке повідомлення стає джерелом для публікації.
  - Acceptance signal: Кандидати `start`, що збігаються, відкривають події за правилом `first arrival wins`, і вибране повідомлення стає канонічним джерелом.
  - Links: Parent epic: M2 Зріз публікації події `start`; [2026-03-14-mvp-delivery-plan.md](active/2026-03-14-mvp-delivery-plan.md)

- [Draft] M2 Вікно придушення дублікатів
  - Type: Story
  - Why it matters: Запобігати повторній публікації між джерелами, зберігаючи документоване правило повторного відкриття через п'ять хвилин.
  - Acceptance signal: Подібні кандидати `start` у межах активного вікна переходять у `suppressed_duplicate`, а відповідний `start` через п'ять хвилин відкриває нову подію.
  - Links: Parent epic: M2 Зріз публікації події `start`; [2026-03-14-mvp-delivery-plan.md](active/2026-03-14-mvp-delivery-plan.md)

- [Draft] M2 Текстова публікація та dry run
  - Type: Story
  - Why it matters: Дати перший видимий для оператора результат без послаблення вимог до шляху публікації та attribution.
  - Acceptance signal: Серіалізований publish worker надсилає текстові пости з attribution, а `DRY_RUN` пригнічує записи в target, зберігаючи той самий шлях ухвалення рішень щодо publication.
  - Links: Parent epic: M2 Зріз публікації події `start`; [2026-03-14-mvp-delivery-plan.md](active/2026-03-14-mvp-delivery-plan.md)

### M3

- [Draft] M3 Повний життєвий цикл події та відновлення
  - Type: Epic
  - Why it matters: Зробити модель події безпечною до перезапусків і операційно надійною після першого зрізу publication.
  - Acceptance signal: Критерії виходу M3 у плані поставки MVP виконані.
  - Links: [2026-03-14-mvp-delivery-plan.md](active/2026-03-14-mvp-delivery-plan.md)

- [Draft] M3 Життєвий цикл сигналу `clear`
  - Type: Story
  - Why it matters: Завершити життєвий цикл події, закриваючи активні події без публікації повідомлень `clear`.
  - Acceptance signal: Сигнали `clear`, що збігаються, закривають лише активні події того самого `event_type`, а незіставлені `clear` переходять у `orphan_clear`.
  - Links: Parent epic: M3 Повний життєвий цикл події та відновлення; [2026-03-14-mvp-delivery-plan.md](active/2026-03-14-mvp-delivery-plan.md)

- [Draft] M3 Відновлення кандидатів і claiming
  - Type: Story
  - Why it matters: Безпечно відновлювати перервану роботу агрегації після перезапуску без дублювання обробки подій.
  - Acceptance signal: Збережені рядки `candidate` повторно захоплюються транзакційно й безпечно відновлюють обробку після перезапуску.
  - Links: Parent epic: M3 Повний життєвий цикл події та відновлення; [2026-03-14-mvp-delivery-plan.md](active/2026-03-14-mvp-delivery-plan.md)

- [Draft] M3 Відновлення публікації та стан retry
  - Type: Story
  - Why it matters: Зберегти намір publication і семантику retry між перезапусками процесу та тимчасовими збоями Telegram.
  - Acceptance signal: Рядки, що залишилися в `selected_for_publish` або `publishing`, перебудовуються в publication jobs, а retry дотримуються зафіксованої політики backoff `5s`, `15s`, `30s`, `60s`, потім обмеження `300s`.
  - Links: Parent epic: M3 Повний життєвий цикл події та відновлення; [2026-03-14-mvp-delivery-plan.md](active/2026-03-14-mvp-delivery-plan.md)

- [Draft] M3 Переходи термінального стану збоїв
  - Type: Story
  - Why it matters: Зробити неретрайні publish failures явними та доступними для запитів і в стані повідомлення, і в стані події.
  - Acceptance signal: Неретрайні publish failures позначають повідомлення як `publish_failed`, а пов'язану подію як `failed` без подальших retry.
  - Links: Parent epic: M3 Повний життєвий цикл події та відновлення; [2026-03-14-mvp-delivery-plan.md](active/2026-03-14-mvp-delivery-plan.md)

### M4

- [Draft] M4 Посилення MVP
  - Type: Epic
  - Why it matters: Підняти сервіс від коректності першого зрізу до повної планки приймання MVP.
  - Acceptance signal: Критерії виходу M4 у плані поставки MVP виконані.
  - Links: [2026-03-14-mvp-delivery-plan.md](active/2026-03-14-mvp-delivery-plan.md)

- [Draft] M4 Публікація фото й підписів
  - Type: Story
  - Why it matters: Розширити зріз publication до мінімальної підтримки медіа, потрібної для MVP.
  - Acceptance signal: Підтримуються пости з фото й підписами, тоді як для альбомів у межах MVP зберігається стратегія першого повідомлення.
  - Links: Parent epic: M4 Посилення MVP; [2026-03-14-mvp-delivery-plan.md](active/2026-03-14-mvp-delivery-plan.md)

- [Draft] M4 Стійкість до copy-forbidden і flood-wait
  - Type: Story
  - Why it matters: Утримувати поведінку publication детермінованою за Telegram-специфічних обмежень доставки.
  - Acceptance signal: Для publication з copy-forbidden виконується fallback до детермінованого тексту attribution `link_only`, а `FloodWaitError` очікує точно повідомлену тривалість перед retry того самого job.
  - Links: Parent epic: M4 Посилення MVP; [2026-03-14-mvp-delivery-plan.md](active/2026-03-14-mvp-delivery-plan.md)

- [Draft] M4 Верифікація місткості та latency
  - Type: Story
  - Why it matters: Довести, що сервіс залишається в межах задокументованого operating envelope MVP.
  - Acceptance signal: Сервіс підтримує щонайменше 100 налаштованих джерел і тримає normal end-to-end latency в межах 10-30 секунд на цільовому профілі VPS, коли flood waits не активні.
  - Links: Parent epic: M4 Посилення MVP; [2026-03-14-mvp-delivery-plan.md](active/2026-03-14-mvp-delivery-plan.md)

- [Draft] M4 Операторське посилення та фінальне приймання
  - Type: Story
  - Why it matters: Завершити MVP із придатними до розгортання runtime-настановами й явним coverage приймання.
  - Acceptance signal: Runtime-настанови охоплюють роботу із secret і reduced-privilege containers, ручні сценарії приймання проходять, а сервіс може працювати 24 години без ручного втручання за нормальних умов.
  - Links: Parent epic: M4 Посилення MVP; [2026-03-14-mvp-delivery-plan.md](active/2026-03-14-mvp-delivery-plan.md)
