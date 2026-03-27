---
name: do-task
description: Execute a canonical planning task in this repository by Planning ID and keep planning statuses aligned. Use when the user invokes `$do-task 0009`, says to do a task by number, or refers to a planning task when only the four-digit ID is known.
---

# Do Task

Resolve a canonical planning task by `Planning ID`, execute the work, and keep the related planning documents consistent.

Use the shared repo helper `bin/find-planning-item` as the source of truth for task lookup. Do not search the planning tree manually unless the helper is unavailable.

This skill can be composed with one role overlay skill: `as-engineer`, `as-tech-lead`, or `as-product-owner`.

## Workflow

1. Run `bin/find-planning-item --json <id>` from the repository root.
2. Read the returned `kind`, `status`, `location`, `path`, and `parents`.
3. Stop if `location` is `archive`; report that the planning item is archived.
4. Stop if `kind` is not `task`; report the resolved type and path.
5. Stop if `status` is `Draft`; propose moving the task to `Ready` before execution.
6. If the task is `Done`, report that it is already complete and do not reopen it unless the user explicitly asks.
7. If the task is `Ready`, implement the task normally.
8. If exactly one role overlay skill is mentioned in the same prompt, apply that role while executing this workflow.
9. If more than one role overlay skill is mentioned, stop and ask the user to choose one role.
10. After implementation and self-check, set the task document to `Done`, update `Last updated`, then recompute the parent story and epic statuses.

## Status Rules

- Canonical active epic, story, and task documents use only `Draft`, `Ready`, and `Done`.
- `Ready` covers both "ready to start" and "currently being worked on".
- Do not introduce `Active` or `Blocked` into canonical active planning docs.
- Do not encode blockers through the `Status:` field.

## Roll-Up Rules

- A task moves to `Done` only after the executor considers the work complete and finishes self-check.
- A story is `Done` only when all child tasks are `Done`; otherwise it stays `Ready`.
- An epic is `Done` only when all child stories are `Done`; otherwise it stays `Ready`.
- If a parent must change status during roll-up, update its `Last updated` field in the same edit.

## Fallbacks

- If `bin/find-planning-item` is unavailable, search `Planning ID: <id>` in `docs/planning/active/` first and `docs/planning/archive/` second.
- Ignore `docs/planning/backlog.md` for numeric task lookup because backlog items do not carry canonical `Planning ID` values.
- Supported role-overlay composition examples: `$as-engineer $do-task 0009`, `$as-tech-lead $do-task 0009`, `$as-product-owner $do-task 0009`.
