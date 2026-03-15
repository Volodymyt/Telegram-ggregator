# План постачання MVP

Status: Draft
Owner: TBD
Last updated: 2026-03-14

## Мета

Перетворити затверджену архітектуру MVP на готовий до постачання дослідницький документ, який пізніше можна буде декомпозувати на конкретні елементи беклогу без повторного відкриття основних рішень реалізації.

## Підсумок

Архітектура вже достатньо стабільна, щоб вести виконання:

- один асинхронний Python-сервіс, який можна розгорнути;
- модульний моноліт, організований за компонентами;
- Telethon для Telegram transport, reconnects і subscriptions;
- Postgres як канонічний persistence layer;
- внутрішній `asyncio.Queue` для processing, candidate aggregation і publishing.

Поточний репозиторій ще не готовий до реалізації. Він усе ще запускає застарілий placeholder entrypoint, не має канонічної структури пакета, не має storage layer, config layer, test harness і execution bridge між архітектурною документацією та planning.

Тому постачання має початися з однієї foundations-віхи, далі пройти через вертикальні end-to-end slices і завершитися hardening для MVP.

Цей документ також має залишатися достатньо конкретним, щоб підтримувати декомпозицію беклогу без повторного відкриття основних технічних рішень під час звичайного виконання.

## Зафіксовані обмеження постачання

Наведені нижче обмеження вже зафіксовані архітектурою та вимогами й не повинні переглядатися під час звичайної декомпозиції завдань:

- Канонічний корінь пакета: `src/telegram_aggregator/`.
- Сервіс лишається одним Python-процесом, який можна розгорнути, для меж MVP.
- Telethon володіє MTProto transport і поведінкою reconnect.
- Postgres є єдиним канонічним джерелом durable state.
- Черги processing, candidate і publish лишаються внутрішніми runtime-примітивами координації.
- `first arrival wins` є канонічним правилом вибору джерела.
- Candidate deduplication працює в межах одного `target_channel` і `event_type`.
- Similarity для candidate використовує `difflib.SequenceMatcher` з порогом `0.82`.
- Повторний відповідний сигнал `start` більш ніж через 5 хвилин після початкового старту події відкриває нову подію.
- Сигнал `clear` закриває лише активну подію того самого `event_type` і ніколи не публікується.
- `DRY_RUN` лишається підтримуваним режимом оператора й має пригнічувати Telegram side effects, не оминаючи intake, filtering, aggregation або persistence logic.
- Restart recovery має покривати довговічну роботу, яка може залишитися зі `classification_status='candidate' and aggregation_status='queued'`, або `publish_status in ('queued', 'publishing')`.

## Висновки дослідження

### Прогалини репозиторію

- `src/Telegram-aggregator/__main__.py` досі є placeholder loop.
- `Dockerfile` досі запускає legacy package замість `src/telegram_aggregator/`.
- `src/telegram_aggregator/` ще не містить цільових runtime-модулів.
- `requirements.txt` досі є placeholder і не задає відтворюваний runtime baseline.
- Немає schema, migration flow, repository layer або реалізації event persistence.
- Немає перевіреного config/settings layer для задокументованого environment і YAML contract.
- Немає worker/runtime bootstrap, login flow, health endpoint або structured observability.
- Немає test harness для filters, deduplication, lifecycle handling і restart recovery.

### Наслідок для постачання

Репозиторій перебуває на до-MVP foundations-етапі. Він не готовий починати безпосередньо з бізнес-функцій. Перша віха має створити виконуваний runtime baseline, перш ніж почнуться функціональні slices.

## Зафіксовані технічні значення за замовчуванням

Ці значення за замовчуванням обрані зараз, щоб прибрати неоднозначність перед декомпозицією беклогу.

### Runtime і структура пакета

- Нову реалізацію будувати лише під `src/telegram_aggregator/`.
- Використовувати один top-level service runtime плюс окремий login entrypoint.
- Організувати код за runtime-компонентами:
  - `bootstrap/`
  - `config/`
  - `storage/`
  - `reading/`
  - `processing/`
  - `candidate_aggregation/`
  - `publishing/`
  - `observability/`

### Зберігання

- Використовувати PostgreSQL з SQLAlchemy 2.x async engine і SQLAlchemy Core, а не ORM models.
- Використовувати Alembic для schema migrations.
- Тримати persistence сфокусованим на `tg_message` і `event`.
- Послідовно застосовувати іменування таблиць:
  - використовувати `snake_case` для всіх database identifiers;
  - використовувати назви таблиць в однині, що семантично відповідають сутності;
  - не використовувати допоміжні суфікси на кшталт `records`;
  - префіксувати таблиці, що зберігають дані походженням із Telegram, через `tg_`.
- Послідовно застосовувати Python naming за PEP 8:
  - використовувати CapWords для класів, типізованих структур та інших type-like objects;
  - використовувати `snake_case` для модулів, функцій, методів, змінних і не-типових ідентифікаторів.
- Моделювати прогрес `tg_message` через незалежні осі статусів замість одного перевантаженого поля статусу повідомлення.
- Для `aggregation_status` і `publish_status` використовувати `new`, коли етап ще не було заплановано, і `queued`, коли повідомлення явно очікує обробки воркером.
- Використовувати transactional row claiming через `SELECT ... FOR UPDATE SKIP LOCKED` для candidate recovery і processing там, де важлива ownership рядків.

### Нормалізація

- Використовувати спільний pipeline нормалізації для filter matching:
  - Unicode normalization з NFKC;
  - приведення до нижнього регістру;
  - обрізання пробілів;
  - згортання повторюваних пробілів;
  - заміна `ё` на `е`.
- Будувати `candidate_signature` з нормалізованого тексту після видалення URL, usernames, punctuation і повторюваних пробілів.
- Матчити лише за текстом повідомлення та media captions.

### Публікація

- Publish worker є єдиним компонентом, якому дозволено публікувати в target channel.
- Поведінка publish за замовчуванням:
  - текстові пости надсилаються як текст із attribution footer;
  - photo posts із captions копіюються, коли це можливо;
  - якщо копіювання заборонене, fallback для MVP це текстовий вивід `link_only` із source attribution замість повторного завантаження медіа.
- Обробка album в MVP залишається зведеною до стратегії first-message.

### Retry і recovery для publish

- Свіжість публікації обмежується `120s` від першої спроби публікації.
- `FloodWaitError` підлягає повторній спробі лише тоді, коли повідомлений час очікування вкладається в залишкове вікно свіжості `120s`; інакше job встановлює `tg_message.publish_status='failed'`, а помилка логується.
- Інші transient publish failures використовують persisted retry state з exponential backoff `5s`, `15s`, `30s`, `60s`, але лише поки наступна спроба все ще вкладається в те саме вікно свіжості `120s`.
- Будь-яка publication job, яка не може завершитися в межах `120s` від першої спроби публікації, встановлює `tg_message.publish_status='failed'`, логує помилку і припиняє retry.
- Non-retriable publish failures встановлюють `tg_message.publish_status='failed'` і для події-власника `publish_status='failed'` без подальших повторних спроб.
- Bootstrap має перебудовувати publication jobs із Postgres для рядків, що лишилися з `publish_status='queued'` або `publish_status='publishing'`, перш ніж steady-state processing вважатиметься healthy.

### Операторський досвід і observability

- Основний login flow: `python -m telegram_aggregator.login`.
- `LOGIN=1` лишається compatibility path для containerized bootstrap.
- За замовчуванням observability складається зі structured JSON logs і lightweight HTTP health endpoint.
- Health endpoint має на високому рівні показувати readiness для Telegram, Postgres і worker liveness.
- Config validation має підтримувати source identifiers у форматі `@username`, `t.me/...` або numeric ids там, де це підтримується, і target identifiers як username або numeric id.
- `DRY_RUN` має виконувати звичайний pipeline до моменту publish decision, пригнічуючи записи в target channel.

### Guardrails для постачання

- Декомпозиція завдань має зберігати трасованість до задокументованого YAML і environment contract, включно з `LOG_LEVEL`, `DRY_RUN`, queue sizes, normalization toggles і login flows.
- Завдання на capacity та operability не повинні знижувати MVP-цілі щонайменше до 100 налаштованих sources, 10-30 секунд нормальної end-to-end latency і невеликого VPS-профілю розгортання `1 vCPU / 512 MB` або краще.
- Operational hardening tasks мають не допускати потрапляння secrets в image і зберігати сумісність із reduced-privilege containers та, де це практично для MVP, з read-only root filesystem.

### Етапність віх

- Перший end-to-end publish slice може бути лише текстовим.
- Підтримка photo-with-caption потрібна для фінальної hardening-віхи MVP, а не для першого вертикального slice.

## Внутрішні контракти, які треба зберегти

Майбутня реалізація та декомпозиція завдань мають зберігати такі внутрішні типи й контракти:

- `CandidateMessage`
- `EventSignal`
- `Event`
- `PublicationJob`
- `tg_message.classification_status`:
  - `pending`
  - `outdated`
  - `filtered_out`
  - `candidate`
- `tg_message.aggregation_status`:
  - `new`
  - `queued`
  - `suppressed_duplicate`
  - `selected`
  - `clear_processed`
  - `orphan_clear`
- `tg_message.publish_status`:
  - `new`
  - `queued`
  - `publishing`
  - `published`
  - `failed`
- `event.state`:
  - `open`
  - `closed`
- `event.publish_status`:
  - `pending`
  - `published`
  - `failed`

## Guardrails для покриття вимог

Ці пункти мають залишатися видимими під час декомпозиції завдань, навіть якщо вони не домінують у назвах віх:

- M0 має покривати config/runtime validation для форматів source і target identifiers, `LOG_LEVEL`, `DRY_RUN`, queue sizes, YAML toggles і обох login entry paths.
- M1 має зберігати `case_insensitive` і normalization-driven поведінку filters із configuration contract, а не лише ядро regex matching.
- M2 має зберігати можливість тестувати `DRY_RUN` і attribution behavior у першому end-to-end publish slice.
- M3 має покривати restart recovery для станів `candidate`, `selected_for_publish` і `publishing`, а не лише recovery для candidate aggregation.
- M4 має включати явну перевірку capacity, latency, runtime security posture і фінальні operator run instructions.

## Робочі потоки

### 1. Foundations

- Вирівнювання канонічного package/runtime.
- Базова лінія залежностей та інструментів.
- Парсинг і валідація config/settings.
- Bootstrap сервісу та життєвий цикл worker'ів.
- Мінімальна observability і health.
- Foundations для test harness.

### 2. Storage

- Налаштування schema і migrations.
- Керування підключеннями.
- Repositories для стану messages і events.
- Ідемпотентні вставки та переходи станів.
- Candidate claiming і restart-safe правила ownership.

### 3. Intake і Processing

- Startup користувацької сесії Telethon.
- Підписка на sources і читання повідомлень.
- Внутрішня нормалізація повідомлень.
- Include/exclude filter engine.
- Processing queue і candidate classification.

### 4. Candidate Aggregation і Event Lifecycle

- Consumer черги candidate.
- Recovery scan для збережених рядків candidate зі `classification_status='candidate'` і `aggregation_status='queued'`.
- Генерація `candidate_signature`.
- Fuzzy matching проти відкритих подій.
- Suppression дублікатів і зв'язування з подіями.
- Обробка `clear` і закриття подій.

### 5. Publishing і Resilience

- Publish queue і serialized publish worker.
- Форматування payload і attribution footer.
- Telethon adapter для publish у target channel.
- Обробка flood wait.
- Restart-safe recovery рядків із `publish_status='queued'` і `publish_status='publishing'`.
- Обробка terminal failures і persisted retry state.
- Fallback-поведінка для випадків, коли копіювання заборонене.

### 6. Operability і Acceptance

- Вирівнювання Docker/runtime.
- Environment і run instructions.
- Перевірка `DRY_RUN`.
- Перевірка health і readiness.
- Перевірка capacity і latency проти MVP operating profile.
- Integration scenarios для restart recovery і deduplication.
- Фінальна перевірка прийняття MVP.

## Віхи

### M0 Foundations Ready

Результат:
- Репозиторій завантажується через канонічний пакет.
- Docker і локальний runtime вказують на той самий контракт entrypoint.
- Dependencies, migrations, config loading, login entrypoint, logging і базова health-перевірка вже на місці.
- Тести можуть запускатися на новій структурі проєкту.

Критерії виходу:
- Сервіс стартує і зупиняється коректно без placeholder code.
- Config validation завершується помилкою одразу на невалідному env або YAML input.
- Config validation покриває формати source і target identifiers, queue sizes, `LOG_LEVEL`, `DRY_RUN`, normalization toggles і login modes.
- Підключення до Postgres і виконання migrations під'єднані.
- Login command створює або перевіряє шлях до session file.

### M1 Intake To Candidate

Результат:
- Нові повідомлення з джерел читаються з Telegram, один раз зберігаються, нормалізуються й позначаються як `outdated`, `filtered_out` або `candidate`.

Критерії виходу:
- Deduplication для повідомлень із джерел працює за `(source_chat_id, source_message_id)`.
- Поведінка filters покриває режими `any` і `all`.
- Поведінка filters покриває `case_insensitive` і normalization toggles з YAML contract.
- Повідомлення, які вже застаріли до класифікації, позначаються як `outdated` без фільтрації або обробки як candidates.
- Candidate classification зберігає `event_type`, `event_signal` і `candidate_signature`.
- Intake і processing на основі черг працюють end-to-end без публікації.

### M2 Start Event Publish Slice

Результат:
- Відповідні `start` candidates відкривають події, пригнічують дублікати між sources і публікують канонічне повідомлення в target channel.

Критерії виходу:
- Правило `first arrival wins` виконується.
- Дубльовані `start` candidates у межах активного вікна стають `suppressed_duplicate`.
- Вибрані повідомлення проходять через `tg_message.publish_status='queued'` до того, як їх забере publish worker.
- Текстова публікація працює з attribution.
- `DRY_RUN` пригнічує записи в target channel, зберігаючи той самий шлях publish decision для перевірки.
- Перший вертикальний slice можна продемонструвати end-to-end.

### M3 Full Event Lifecycle And Recovery

Результат:
- Система обробляє сигнали `clear`, restart recovery, persisted claiming кандидатів і переходи станів під час збоїв публікації.

Критерії виходу:
- Відповідний `clear` закриває активну подію і не публікується.
- Невідповідний `clear` стає `orphan_clear`.
- Restart recovery сканує збережені рядки candidate, що очікують агрегації, і рядки публікації з `publish_status in ('queued', 'publishing')` та відновлює роботу без дубльованої публікації.
- Publish status і terminal failures зберігаються і в рядках `tg_message`, і в рядках `event`.
- Transient publish failures ідуть за зафіксованою політикою backoff, зупиняються після `120s` від першої спроби публікації та логують terminal timeout failures.

### M4 MVP Hardening

Результат:
- Сервіс досягає задокументованої планки прийняття MVP для media support, resilience і operability.

Критерії виходу:
- Підтримуються photo posts із captions.
- Fallback для copy-forbidden поводиться детерміновано.
- Обробка flood wait і обмежене вікно retry `120s` покриті перевірками.
- Сервіс підтримує щонайменше 100 налаштованих sources на цільовому deployment profile.
- Нормальна end-to-end latency лишається в межах 10-30 секунд, коли flood waits не активні.
- Runtime guidance покриває роботу із secrets і reduced-privilege container operation.
- Задокументовані manual acceptance scenarios проходять.
- Runtime можна експлуатувати 24 години без ручного втручання за нормальних умов.

## Правила залежностей для майбутньої декомпозиції завдань

- Розбивай роботу спочатку за віхами, а потім за workstream.
- Кожне майбутнє завдання має називати один primary implementation component і один acceptance signal.
- Не створюй cross-component tasks, якщо робота не є foundational, storage-related або operational.
- Candidate aggregation лишається єдиним місцем, де дозволено deduplicate candidates, керувати event lifecycle і створювати publication jobs.
- Publish behavior лишається ізольованою в publish worker і publisher adapter.
- Архітектурні інваріанти з цього документа треба вважати зафіксованими значеннями за замовчуванням, якщо їх не змінено через ADR.

## Матриця тестування та прийняття

Пізніший task backlog має явно покривати такі сценарії:

- невалідна конфігурація завершується помилкою під час startup;
- startup працює з наявним session file;
- одноразовий login працює без session file;
- дубльовані source messages безпечно ігноруються;
- include і exclude filters працюють і в режимі `any`, і в режимі `all`;
- зміни нормалізації впливають на matching лише через задокументований pipeline;
- застарілі повідомлення з джерел позначаються як `outdated` до оцінювання фільтрів;
- `DRY_RUN` пригнічує target publication, не оминаючи логіку publish decision;
- схожі `start` messages у межах 5 хвилин мапляться на одну подію;
- повторний `start` через 5 хвилин відкриває нову подію;
- `clear` закриває лише активну подію того самого `event_type`;
- restart recovery безпечно відновлює рядки candidate, що очікують агрегації, і рядки публікації в станах `queued` або `publishing`;
- publish failures коректно оновлюють persisted state;
- transient publish retries ідуть за зафіксованою політикою backoff лише в межах `120s` від першої спроби публікації;
- publication jobs, які перевищують вікно свіжості публікації `120s`, логуються і зберігаються з `tg_message.publish_status='failed'`;
- text і photo-with-caption flows відповідають планці прийняття MVP.

## Поза межами цього плану

- Детальне розбиття на спринти.
- Календарні оцінки.
- Розподіл команди за staffing.
- Post-MVP теми дорожньої карти, такі як UI, кілька target channels, moderation або external brokers.
