---
name: generate-story-briefs
description: Generate missing human-only story briefs for this repository by finding active canonical stories without `brief.uk.md`, then delegating one story per cheap worker agent that writes the brief directly from the canonical story and the shared format contract. Use when asked to mass-create story briefs, find stories missing briefs and generate them, or backfill `brief.uk.md` files in parallel.
---

# Generate Story Briefs

Use this skill only for this repository's canonical planning tree.

## Sources Of Truth

- Use `bin/find-stories-missing-briefs --json` as the only selector for stories that need a brief.
- Use `docs/planning/story-brief-format.md` as the only brief-format contract.
- Use each canonical story document returned by the selector as the only content source for that story's brief.

## Workflow

1. Run `bin/find-stories-missing-briefs --json` from the repository root.
2. If the selector returns an empty list, report that all active non-Done stories already have `brief.uk.md` and stop.
3. Treat every returned item as required work. Process both `Draft` and `Ready` stories.
4. Do not read every story into the main context up front. Keep the main context limited to the selector output and the format contract.
5. Split the returned stories into batches of four.
6. For each story in the current batch, spawn one `worker` agent with:
   - `model: gpt-5.4-mini`
   - `fork_context: false`
   - ownership of exactly one target file: the returned `missing_brief_path`
7. In each worker prompt, pass:
   - the canonical `story_path`
   - the target `missing_brief_path`
   - `docs/planning/story-brief-format.md`
   - an instruction to read the story and the format contract, then write `brief.uk.md` directly
8. Tell each worker that it is not alone in the codebase and must not edit or revert any file except its owned `brief.uk.md`.
9. After spawning a batch, wait for completions, review results, then move to the next batch.
10. After each worker finishes, validate the created brief locally before accepting it.
11. If a brief is close but invalid, do a minimal local fix or send one correction follow-up to that worker.
12. If one worker fails, continue processing the rest. At the end, report both the successful stories and any remaining failures.

## Worker Prompt Contract

Every worker prompt should enforce these rules:

- Read only the assigned canonical story and `docs/planning/story-brief-format.md`.
- Create or update only the assigned `brief.uk.md`.
- Write the brief in Ukrainian.
- Follow the required Markdown structure exactly.
- Keep the brief short and human-scannable.
- Derive the checklist from the story's existing `Goal`, `Scope`, `Steps`, and `Acceptance Criteria`.
- Do not add new scope, requirements, dependencies, or acceptance conditions.
- Do not copy large sections verbatim from the canonical story.
- Do not include forbidden metadata such as `Planning ID`, `Status`, `Last updated`, `Links`, or `Risks`.

## Validation Rules

Accept a worker result only if all of the following are true:

- `brief.uk.md` exists at the exact assigned path.
- The file starts with `# Бриф`.
- The file contains `## Коротко` and `## Що потрібно зробити`.
- The checklist uses Markdown checkboxes and stays concise.
- The brief is consistent with the canonical story and does not introduce new requirements.
- The brief does not include forbidden metadata or long copied sections.

## Guardrails

- Do not invent a second selector or a second brief-format document.
- Do not generate briefs for epics, tasks, archived stories, or already-complete stories.
- Do not collapse multiple stories into one worker task.
- Do not ask workers to return draft text when they can write their owned `brief.uk.md` directly.
- Do not let one failed worker block the rest of the batch.
