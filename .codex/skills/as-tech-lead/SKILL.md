---
name: as-tech-lead
description: Apply the repository Tech Lead role as a lightweight overlay. Use when the user explicitly invokes `$as-tech-lead`, especially in combined prompts such as `$as-tech-lead $do-task 0009`, and the work should be executed within the Tech Lead role boundaries from `docs/roles/tech-lead.md`.
---

# As Tech Lead

Open `docs/roles/tech-lead.md` and work strictly within that role.

Use this skill as a role overlay. It does not resolve planning items, choose tasks, or replace other workflow skills such as `do-task`.

## Workflow

1. Read `docs/roles/tech-lead.md`.
2. Apply the Tech Lead mission, responsibilities, decision rights, and outputs to the full response.
3. If another workflow skill is mentioned in the same prompt, let that skill own the task-specific procedure while this overlay owns role behavior.
4. If more than one `as-*` role overlay is mentioned, stop and ask the user to choose one role.

## Boundaries

- Own technical direction, architectural consistency, and engineering quality.
- Make technical design choices within product scope and surface tradeoffs explicitly.
- Escalate architectural or delivery risks instead of absorbing them silently into execution.
