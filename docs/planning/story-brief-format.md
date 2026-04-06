# Story Brief Format

This document defines the human-only brief format for canonical story documents.

## Purpose

- Give a human reader a short, scannable summary of one story.
- List the concrete work as a checklist in Ukrainian.
- Keep the canonical story document as the only source of truth for planning decisions.

## Scope

- Create one brief for each canonical story document.
- Do not create briefs for epics.
- Do not create briefs for tasks.
- Do not create briefs for top-level date-prefixed delivery plans.

## File Naming And Placement

- Use the exact filename `brief.uk.md`.
- Place the file in the same directory as the canonical story document.
- For active work, use the path `docs/planning/active/<epic_dir>/<story_dir>/brief.uk.md`.
- Keep the same filename when the story moves to `docs/planning/archive/`.
- Do not add `Planning ID` values, order prefixes, or slug variants to the brief filename.

## Canonical Relationship To Story Docs

- The canonical story document `<id>_<short_title>.md` remains the source of truth.
- The brief is a human-only companion document and is not a canonical planning item.
- The brief must not introduce new scope, requirements, dependencies, or acceptance conditions.
- The brief must summarize only what already exists in the canonical story document.
- If the brief conflicts with the canonical story document, fix the brief to match the canonical story document.

## Required Brief Template

Every story brief must use this structure:

```md
# Бриф

## Коротко

<1-2 short sentences in Ukrainian>

## Що потрібно зробити

- [ ] <concrete action 1>
- [ ] <concrete action 2>
- [ ] <concrete action 3>
```

## Writing Rules

- Write the brief in Ukrainian.
- Keep the brief short enough to read in one quick pass.
- Keep the `## Коротко` section to one or two short sentences.
- Make the checklist the main content of the brief.
- Use between three and seven checklist items unless the story is exceptionally small.
- Start each checklist item with a verb.
- Describe observable implementation work, not vague intent.
- Keep checklist items specific enough that an engineer can act on them without rereading the whole story first.
- Preserve the same meaning as the canonical story `Goal`, `Scope`, `Steps`, and `Acceptance Criteria`.

## Optional Sections

Use optional sections only when they prevent likely misreading of the story.

Allowed optional sections:

- `## Не робимо`
- `## Готово коли`

If both optional sections are present, place them in this order:

1. `## Не робимо`
2. `## Готово коли`

### `## Не робимо`

Use this section only when the story has important non-goals that are easy to violate during implementation.

Rules:

- List only the most important boundaries.
- Keep the list short.
- Do not restate the entire `Scope` section.

### `## Готово коли`

Use this section only when the desired completion signal is not obvious from the checklist alone.

Rules:

- Use short result-oriented bullets.
- Summarize only the most important acceptance signals.
- Do not copy the full acceptance criteria verbatim.

## Forbidden Content

Do not include any of the following in a brief:

- `Planning ID`
- `Status`
- `Last updated`
- `Milestone`
- Full `Links` sections
- Full `Risks` sections
- Full `Scope` sections copied verbatim
- Full `Acceptance Criteria` copied verbatim
- Long rationale or historical context
- New requirements that do not exist in the canonical story

## Synchronization Rules

- Generate or update the brief only from the canonical story document.
- Update the brief when the story changes in a way that affects human execution guidance.
- Prefer rewriting a brief for clarity over appending patch notes.
- Keep the brief stable in structure even if the canonical story grows.
- Do not use the brief as the source for updating the canonical story.

## Example

```md
# Бриф

## Коротко

Потрібно додати спільний рушій нормалізації та фільтрації для тексту повідомлень і підписів до медіа.
Також потрібно зафіксувати в конфігу явне правило, після якого повідомлення вважається застарілим.

## Що потрібно зробити

- [ ] Додати спільні хелпери нормалізації для тексту повідомлень і підписів до медіа.
- [ ] Реалізувати перевірку include та exclude груп у порядку конфігурації.
- [ ] Підтримати режими `any` і `all` та правило `first matching group wins`.
- [ ] Додати в YAML-контракт `runtime.classification_stale_after_seconds`.
- [ ] Оновити валідацію конфігу та приклади для нового runtime-поля.
- [ ] Додати тести на нормалізацію, порядок груп, режим `all` і порожній `exclude`.

## Не робимо

- Не додаємо збереження статусів у базу в межах цієї story.
- Не реалізуємо публікацію або агрегацію подій.

## Готово коли

- Поведінка фільтрації збігається з канонічною story.
- Нове runtime-поле є обов'язковим і проходить перевірку.
```

## Anti-Patterns

Avoid these mistakes when writing or generating a brief:

- Turning the brief into a translated copy of the full story document.
- Writing vague checklist items such as "support the feature" or "handle edge cases".
- Adding implementation details that the canonical story does not require.
- Copying large blocks from `Scope` or `Acceptance Criteria`.
- Using the brief to record progress, blockers, or execution status.
