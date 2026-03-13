# Project Requirements

## Functional Requirements

### Sources

- Sources are configured through a file-based configuration format and environment variables.
- Each source may be provided as `@channel_username`, `t.me/...`, or numeric identifier where supported.
- The service must support at least 100 source channels or chats.
- The service must connect to Telegram through Telethon, register new-message handlers, and process incoming messages in near real time.

### Filtering

- Filtering must support include and exclude rules.
- Include rules must support regex patterns and pipe-separated OR expressions.
- Each include rule must define `pattern`, `event_type`, and `event_signal`.
- `event_signal` must support `start` and `clear`.
- Exclude rules must support regex patterns.
- Filter mode must support `any` and `all`.
- Matching must inspect both message text and media captions.
- Normalization must be configurable and may include lowercasing, whitespace trimming, and character normalization such as `ё` to `е`.
- In `any` mode, the first matched include rule in configuration order defines the candidate `event_type` and `event_signal`.
- In `all` mode, all include rules must share the same `event_type` and `event_signal`, otherwise configuration validation must fail.

### Repost Behavior

- Matching `start` candidates selected by the candidate aggregator must be published to the target Telegram channel.
- Text posts must preserve message text.
- Media posts should preserve media and caption when possible.
- Reposts must include attribution to the source and a post link when available.
- If forwarding or copying is restricted, the service must follow a configured fallback policy.
- Album handling may be reduced in the MVP to a first-message strategy.
- `clear` candidates must close an active event of the same `event_type` and must not be published.

### Deduplication

- The service must persist source messages, candidate state, and logical event state in Postgres.
- The service must not repost the same message more than once.
- The primary source-message deduplication key is `(source_chat_id, message_id)`.
- Candidate aggregation must also prevent publishing the same logical event more than once across multiple sources.
- Logical-event deduplication must operate within the same `target_channel` and `event_type`.
- The candidate aggregator must use fuzzy similarity of normalized candidate content to match candidates to open events.
- The default similarity implementation must use Python `difflib.SequenceMatcher` with a ratio threshold of `0.82`.
- A repeated matching `start` candidate more than 5 minutes after the original event start must open a new logical event.
- The canonical source for publication must be the first candidate that opens the event.
- A link-based signal may strengthen similarity when available, but it must not be the only cross-source deduplication strategy.
- Deduplication state must persist across restarts.

### Resilience

- The service must reconnect automatically after session interruption.
- Flood wait conditions must be handled by waiting for the required duration.
- Transient failures must use backoff behavior.
- The candidate aggregator must recover unprocessed `candidate` rows from Postgres after restart.
- Publishing must be serialized through an internal queue with throttling to reduce rate-limit pressure.

### One-Time Authorization

- On first startup without a session file, the service must support a one-time login flow.
- The supported operator flows are:
  - interactive login mode controlled by `LOGIN=1`, or
  - a separate login command such as `python -m telegram_aggregator.login`.

## Non-Functional Requirements

### Performance

- Normal end-to-end delay from source message arrival to repost should remain within 10 to 30 seconds when flood waits are not active.
- The target deployment profile is a small VPS with 1 vCPU and 512 MB or more of RAM.

### Reliability

- After restart, the service must continue operating from persisted deduplication state.
- Logs must be structured, either as JSON or consistent key-value output.

### Security

- Telegram secrets must not be baked into the image.
- `api_id`, `api_hash`, and the session file must be provided through environment variables and mounted storage.
- The container should support reduced privileges and may optionally use a read-only root filesystem.
- A 2FA password must not be stored in plain text.

## External Configuration Contract

### Environment Variables

- `TG_API_ID`: Telegram API ID.
- `TG_API_HASH`: Telegram API hash.
- `TG_SESSION_PATH`: path to the persisted Telegram session file, for example `/data/session.session`.
- `DATABASE_URL`: Postgres connection string for message, candidate, and event-state persistence.
- `TARGET_CHANNEL`: username or numeric identifier of the destination channel.
- `CONFIG_PATH`: path to the file-based service configuration.
- `LOG_LEVEL`: runtime log level such as `INFO`, `DEBUG`, or `WARNING`.
- `DRY_RUN`: optional mode that logs matches without publishing.
- `LOGIN`: optional mode that triggers one-time interactive authorization.

### Configuration File

The target configuration shape is:

```yaml
sources:
  - "@channel1"
  - "@channel2"

filters:
  mode: any
  include:
    - pattern: "Київ|Спуск|Балістика"
      event_type: ballistic
      event_signal: start
    - pattern: "чисто"
      event_type: ballistic
      event_signal: clear
  exclude:
    - "реклама|підписуйтесь"
  case_insensitive: true
  normalize: true

repost:
  add_source_footer: true
  footer_template: "Джерело: {source}\n{link}"
  fallback_on_copy_forbidden: "link_only"

runtime:
  processing_queue_size: 1000
  candidate_queue_size: 1000
  publish_queue_size: 200
  candidate_similarity_threshold: 0.82
  event_reopen_window_seconds: 300
  candidate_recovery_scan_seconds: 15
```

## Testing And Acceptance

### Unit Coverage

- Filter logic must cover `any` and `all` modes.
- Exclude rules must block matching messages.
- Case-insensitive and normalization behavior must be verified.
- Source-message deduplication must reject repeated processing of the same message.
- Candidate aggregation must suppress duplicate logical events across multiple sources.
- `clear` processing must close only an active event of the same `event_type`.
- Restart recovery must reprocess persisted candidates that were not yet aggregated.

### Manual Integration Scenario

- Given two source channels and a filter that matches `Київ|Спуск|Балістика`
- When one source publishes a matching `start` message and another source publishes a similar message within 5 minutes
- Then the target channel receives a repost with attribution
- And only the first matching source is published
- And restarting the container does not create a duplicate repost

- Given an active logical event for `event_type=ballistic`
- When a matching `clear` message arrives
- Then the event is closed in persistence
- And no new target-channel post is created

### MVP Acceptance Criteria

- The service runs for at least 24 hours without manual intervention.
- The service republishes at least text messages and photo posts with captions.
- Deduplication works across restarts and across multiple sources for the same event.
- All runtime parameters come from environment variables and configuration.
- Delivery includes a Docker image and run instructions.
