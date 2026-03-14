# Backlog

This document stores prioritized work that is not yet active.

## Status Model

Use one of the following statuses for each item:

- `Draft`
- `Ready`
- `Blocked`
- `Done`
- `Archived`

## Planning Item Types

- `Epic`: A large outcome-oriented planning item that groups related stories.
- `Story`: A testable delivery slice within one epic that can be decomposed into tasks.
- `Task`: The smallest execution item within one story that describes concrete implementation work.

Use the hierarchy `epic > story > task` during decomposition.

## Title Lineage Convention

Encode ancestor relationships directly in the item title by using planning file stems in square brackets.

```md
- [Status] Epic title
- [Status][2026-03-14-epic-example-epic] Story title
- [Status][2026-03-14-epic-example-epic][2026-03-14-story-example-story] Task title
```

- Use only ancestor file stems, without `.md` or directory names.
- Order bracket segments from the highest ancestor to the nearest ancestor.
- Do not include the current item's own file stem in its title.
- If an ancestor does not have its own planning file yet, omit that bracket segment until the file exists.

## Item Template

Use a compact format for each backlog item:

```md
- [Status][ancestor-file-stem-1][ancestor-file-stem-2] Short title
  - Type: Epic | Story | Task
  - Why it matters:
  - Acceptance signal:
  - Links:
```

## Maintenance Rule

- Keep the list prioritized from top to bottom.
- Keep title lineage aligned with current planning filenames when linked ancestor files exist.
- Move active execution plans into [`active/`](active/README.md).
- Move completed or superseded work into [`archive/`](archive/README.md).
