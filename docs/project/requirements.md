# Project Requirements

## Functional Requirements

### Sources

- Sources are configured through a file-based configuration format and environment variables.
- Each source may be provided as `@channel_username`, `t.me/...`, or numeric identifier where supported.
- The service must support at least 100 source channels or chats.
- The service must connect to Telegram, subscribe to new message events, and process incoming messages in near real time.

### Filtering

- Filtering must support include and exclude rules.
- Include rules must support regex patterns and pipe-separated OR expressions.
- Exclude rules must support regex patterns.
- Filter mode must support `any` and `all`.
- Matching must inspect both message text and media captions.
- Normalization must be configurable and may include lowercasing, whitespace trimming, and character normalization such as `ё` to `е`.

### Repost Behavior

- Matching messages must be published to the target Telegram channel.
- Text posts must preserve message text.
- Media posts should preserve media and caption when possible.
- Reposts must include attribution to the source and a post link when available.
- If forwarding or copying is restricted, the service must follow a configured fallback policy.
- Album handling may be reduced in the MVP to a first-message strategy.

### Deduplication

- The service must not repost the same message more than once.
- The primary deduplication key is `(source_chat_id, message_id)`.
- A link-based key may be used when available.
- Deduplication state must persist across restarts.

### Resilience

- The service must reconnect automatically after session interruption.
- Flood wait conditions must be handled by waiting for the required duration.
- Transient failures must use backoff behavior.
- Publishing must be serialized through an internal queue with throttling to reduce rate-limit pressure.

### One-Time Authorization

- On first startup without a session file, the service must support a one-time login flow.
- The supported operator flows are:
  - interactive login mode controlled by `LOGIN=1`, or
  - a separate login command such as `python -m app.login`.

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
    - "Київ|Спуск|Балістика"
  exclude:
    - "реклама|підписуйтесь"
  case_insensitive: true
  normalize: true

repost:
  add_source_footer: true
  footer_template: "Джерело: {source}\n{link}"
  fallback_on_copy_forbidden: "link_only"

dedup:
  db_path: /data/state.db
```

## Testing And Acceptance

### Unit Coverage

- Filter logic must cover `any` and `all` modes.
- Exclude rules must block matching messages.
- Case-insensitive and normalization behavior must be verified.
- Deduplication must reject repeated processing of the same message.

### Manual Integration Scenario

- Given two source channels and a filter that matches `Київ|Спуск|Балістика`
- When a source publishes a matching message
- Then the target channel receives a repost with attribution
- And restarting the container does not create a duplicate repost

### MVP Acceptance Criteria

- The service runs for at least 24 hours without manual intervention.
- The service republishes at least text messages and photo posts with captions.
- Deduplication works across restarts.
- All runtime parameters come from environment variables and configuration.
- Delivery includes a Docker image and run instructions.
