---
name: sync-docs-ua-translations
description: Sync Ukrainian documentation translations for this repository by comparing modification times between `docs/` and `docs_ua/` and retranslating only stale or missing Markdown files on request. Use when asked to refresh, sync, or update `docs_ua` after edits in `docs/`, or when asked to translate changed documentation files instead of retranslating the whole tree.
---

# Sync Docs UA Translations

Use this skill only for this repository's mirrored documentation trees: `docs/` as the source of truth and `docs_ua/` as the Ukrainian translation target.

## Workflow

1. Run `python3 scripts/list_stale_translations.py --repo-root <repo-root>` from this skill directory or by using the script's absolute path.
2. Read the JSON output and treat each item as a required translation update.
3. If the list is empty, report that `docs_ua/` is already up to date and stop.
4. For each stale item:
   - translate the source file into Ukrainian,
   - write it to the mirrored path under `docs_ua/`,
   - create parent directories when needed,
   - leave all other translated files untouched.
5. Confirm that `.codexignore` contains `docs_ua/`. Add it only if the entry is missing.

## Translation Rules

- Preserve Markdown structure exactly: headings, lists, code fences, tables, block quotes, and relative link shapes.
- Keep technical tokens unchanged: paths, environment variables, package names, identifiers, regex fragments, YAML keys, schema field names, code symbols, and status literals that act as machine-facing tokens.
- Rewrite internal documentation links so translated files remain self-contained within `docs_ua/`.
- Translate human-readable labels inside Mermaid diagrams, but do not change Mermaid syntax, participant aliases, node identifiers, or other technical tokens that would break the diagram.
- Preserve the same relative file layout from `docs/` to `docs_ua/`.

## Staleness Rules

- A file is stale when the mirrored target file does not exist.
- A file is stale when `mtime(source) > mtime(target)`.
- A file is not stale when `mtime(source) <= mtime(target)`.
- Ignore files that exist only in `docs_ua/`; do not delete them.

## Guardrails

- Do not retranslate the whole tree when only a subset is stale.
- Do not use Git diff or content similarity as the freshness rule for this skill; use filesystem modification time only.
- Do not rewrite unrelated documentation outside `docs_ua/`.
- Do not modify `docs/` source files while syncing translations.
