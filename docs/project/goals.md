# Project Goals

## Product Goals

- Aggregate selected Telegram sources into a single target channel automatically.
- Reduce manual monitoring effort by filtering incoming posts with configurable keyword and regex rules.
- Preserve useful source context by adding attribution and links where available.

## Operational Goals

- Run continuously as a simple daemonized service in Docker.
- Keep deployment manageable through environment variables, file-based configuration, and mounted state.
- Provide minimal observability through structured logs and a health-check mechanism.

## Technical Quality Goals

- Persist repost state so duplicate messages are not published after restart.
- Operate reliably against Telegram disconnects and flood-wait conditions.
- Remain lightweight enough for a small VPS deployment target.

## In Scope For MVP

- Listening to source channels and chats.
- Filtering by include and exclude rules.
- Publishing to one target channel.
- Deduplication backed by SQLite.
- Containerized delivery with `Dockerfile` and a basic Compose example.
- Minimal administration, logging, and health monitoring.

## Out Of Scope For MVP

- Web UI for rule management.
- ML-based classification or semantic search.
- Multiple target channels.
- Moderation workflow with approval queue.
- Postgres or Redis as a required dependency for the first release.

## Success Criteria

- The service republishes matching content from configured sources to the target channel.
- The service handles at least text messages and photos with captions.
- Duplicate reposts are prevented across restarts.
- All runtime parameters come from environment variables and configuration files.
- The packaged service can operate for 24 hours without manual intervention under normal conditions.
