# Glossary

Use this document to define project-specific terms, abbreviations, and domain language.

## Terms

- `Telegram-ggregator`: Working repository and service name for the Telegram reposting service.
- `Source channel`: A Telegram channel or chat from which the service reads incoming messages.
- `Target channel`: The Telegram channel that receives reposted content.
- `Filter rule`: A configured include or exclude matching rule based on keywords or regex patterns.
- `Typed include rule`: An include rule that carries `pattern`, `event_type`, and `event_signal`.
- `Candidate message`: A source message that matched one typed include rule and is awaiting event-level aggregation.
- `Event signal`: Lifecycle meaning attached to a typed include rule. The MVP supports `start` and `clear`.
- `Event type`: A configured logical category such as `ballistic`, `missile`, or `drone`.
- `Logical event`: A grouped threat event that may contain several candidate messages from different sources.
- `Canonical source`: The first candidate that opens a logical event and becomes the publication source for that event.
- `Orphan clear`: A `clear` candidate that does not match any currently open event of the same type.
- `Repost`: Publishing selected source content into the target channel.
- `Attribution`: Source reference added to the repost, typically including the source name and post link.
- `Deduplication`: Logic that prevents repeated publication of the same source message or the same logical event.
- `FloodWait`: Telegram-imposed wait period after a rate limit is hit.
- `User session`: Persisted authenticated Telegram account session used for MTProto access.
- `Dry run`: Execution mode in which matches are logged but not published.
- `Epic`: A large outcome-oriented planning item that groups related stories.
- `Story`: A testable delivery slice within one epic that can be decomposed into tasks.
- `Task`: The smallest execution planning item within one story that describes concrete implementation work.

Use the hierarchy `epic > story > task` during planning decomposition.

Add new entries when a term could be interpreted differently by engineers, operators, or stakeholders.
