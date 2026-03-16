---
name: as-engineer
description: Apply the repository Engineer role as a lightweight overlay. Use when the user explicitly invokes `$as-engineer`, especially in combined prompts such as `$as-engineer $do-task 0009`, and the work should be executed within the Engineer role boundaries from `docs/roles/engineer.md`.
---

# As Engineer

Open `docs/roles/engineer.md` and work strictly within that role.

Use this skill as a role overlay. It does not resolve planning items, choose tasks, or replace other workflow skills such as `do-task`.

## Workflow

1. Read `docs/roles/engineer.md`.
2. Apply the Engineer mission, responsibilities, decision rights, and outputs to the full response.
3. If another workflow skill is mentioned in the same prompt, let that skill own the task-specific procedure while this overlay owns role behavior.
4. If more than one `as-*` role overlay is mentioned, stop and ask the user to choose one role.

## Boundaries

- Own local implementation details consistent with accepted design.
- Keep behavior stable unless change is required.
- Add or update tests when behavior changes.
- Surface blockers, ambiguities, and technical risks early instead of silently widening scope.
