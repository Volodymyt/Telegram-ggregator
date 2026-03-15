# Active Plans

This directory stores active planning items.

## Layout

- Top-level delivery or investigation plans that span multiple milestones stay as date-prefixed files in this directory.
- Each active epic lives in its own directory named `{order}_{id}_{short_title}`.
- Each epic directory contains one canonical epic file named `{id}_{short_title}.md`.
- Each story lives directly inside its parent epic directory as `{order}_{id}_{short_title}`.
- Each story directory contains one canonical story file named `{id}_{short_title}.md`.
- Each task lives as a Markdown file inside the parent story `tasks/` directory using `{order}_{id}_{short_title}.md`.

Example:

```text
docs/planning/active/
  2026-03-14-mvp-delivery-plan.md
  01_0001_foundations_ready/
    0001_foundations_ready.md
    01_0002_runtime_package_contract/
      0002_runtime_package_contract.md
    03_0012_storage_foundation/
      0012_storage_foundation.md
      tasks/
        01_0013_storage_surface_alembic.md
```

## Naming Rules

- Use lowercase ASCII `snake_case` for all slugs in directory names and filenames.
- Use stable two-digit `order` numbers for execution priority within one sibling set: epic directories are ordered within `active/`, story directories are ordered within their parent epic, and task files are ordered within their parent story.
- Use stable four-digit `Planning ID` values for canonical epic, story, and task identity across `active/` and `archive/`.
- Epic and story directories use `{order}_{id}_{short_title}`.
- Epic and story files use `{id}_{short_title}.md`.
- Task files use `{order}_{id}_{short_title}.md`.
- `Planning ID` must never change after assignment.
- Reprioritization may change local `order`, but it must not change `Planning ID`.
- Do not renumber existing items just to close gaps after removal or archive moves; renumber only when you intentionally change execution priority.

## Canonical Files And IDs

- Epic directories must contain exactly one canonical epic document named `{id}_{short_title}.md`.
- Story directories must contain exactly one canonical story document named `{id}_{short_title}.md`.
- Task files are canonical directly and do not have a separate task directory per item.
- Record `Planning ID` directly under the document title in every canonical epic, story, and task document.
- Record `Milestone` directly under the document title only for epic documents.
- `breakdown.md` is optional for epic and story directories and should exist only when extra investigation or decomposition detail is needed.
- Create `tasks/` only when a story is decomposed into executable tasks.
- Do not create task subdirectories.
- Top-level plan files are linked by path and do not receive `Planning ID` values.
- Assign the next `Planning ID` as `max(existing active/archive Planning ID) + 1`.

## Suggested Template

```md
# Title

Planning ID: 0001
Milestone: M0
Status: Active
Last updated:

## Goal

## Scope

## Steps

## Risks

## Acceptance Criteria

## Links
```
