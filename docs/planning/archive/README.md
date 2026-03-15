# Planning Archive

Store completed, cancelled, or superseded planning documents in this directory.

## Archive Rule

- Preserve the original plan content.
- Add a short note at the top if the plan was cancelled or replaced.
- Keep top-level plan filenames stable when moving them from [`active/`](../active/README.md).
- Keep canonical epic and story directory names stable when moving planning trees from `active/` to `archive/`.
- Keep canonical internal filenames stable inside archived planning trees: `{id}_{short_title}.md`, optional `breakdown.md`, and task filenames `{order}_{id}_{short_title}.md`.
- Archive moves must not change `Planning ID` values or local sibling order unless the archive note explicitly documents a deliberate reprioritization snapshot.
