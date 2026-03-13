# Glossary

Use this document to define project-specific terms, abbreviations, and domain language.

## Terms

- `Telegram-ggregator`: Working repository and service name for the Telegram reposting service.
- `Source channel`: A Telegram channel or chat from which the service reads incoming messages.
- `Target channel`: The Telegram channel that receives reposted content.
- `Filter rule`: A configured include or exclude matching rule based on keywords or regex patterns.
- `Repost`: Publishing selected source content into the target channel.
- `Attribution`: Source reference added to the repost, typically including the source name and post link.
- `Deduplication`: Logic that prevents the same source message from being published more than once.
- `FloodWait`: Telegram-imposed wait period after a rate limit is hit.
- `User session`: Persisted authenticated Telegram account session used for MTProto access.
- `Dry run`: Execution mode in which matches are logged but not published.

Add new entries when a term could be interpreted differently by engineers, operators, or stakeholders.
