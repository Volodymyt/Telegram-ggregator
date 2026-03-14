# Active Plans

This directory stores active planning items.

## Layout

- Top-level delivery or investigation plans that span multiple milestones stay as date-prefixed files in this directory.
- Each active epic lives in its own directory named `{milestone_key}_{epic_seq}_{short_title}`.
- Each story lives directly inside its parent epic directory as `{story_seq}_{short_title}`.
- Each task lives as a Markdown file inside the parent story `tasks/` directory.

Example:

```text
docs/planning/active/
  2026-03-14-mvp-delivery-plan.md
  m0_01_foundations_ready/
    epic.md
    01_runtime_package_contract/
      story.md
    03_storage_bootstrap/
      story.md
      tasks/
        01_storage_surface_alembic.md
```

## Naming Rules

- Use lowercase ASCII `snake_case` for all directory names and task filenames.
- Use stable two-digit sequence numbers for `epic`, `story`, and `task` ordering: `01`, `02`, `03`.
- Epic directories use `{milestone_key}_{epic_seq}_{short_title}`.
- Story directories use `{story_seq}_{short_title}`.
- Task files use `NN_short_title.md`.
- Do not renumber existing items to close sequence gaps after removal or archive moves.

## Canonical Files And IDs

- Epic directories must contain `epic.md` as the canonical epic document.
- Story directories must contain `story.md` as the canonical story document.
- `breakdown.md` is optional for epic and story directories and should exist only when extra investigation or decomposition detail is needed.
- Create `tasks/` only when a story is decomposed into executable tasks.
- Do not create task subdirectories.
- Backlog lineage must use ancestor directory IDs, not filenames.
- Top-level plan files are linked by path and are not used as lineage IDs.

## Suggested Template

```md
# Title

Status: Active
Last updated:

## Goal

## Scope

## Steps

## Risks

## Acceptance Criteria

## Links
```
