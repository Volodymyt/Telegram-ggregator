# Documentation

This directory is the entry point for internal project documentation.

## Structure

- `project/` stores stable project knowledge that changes infrequently.
- `planning/` stores roadmap, backlog, active work items, and archived plans.
- `roles/` stores role definitions, ownership boundaries, and collaboration expectations.
- `adr/` stores architecture and process decisions that should remain discoverable.

## Placement Rules

- Put long-lived product and technical context in `project/`.
- Put operational planning artifacts in `planning/`.
- Put responsibility models and decision boundaries in `roles/`.
- Put important decisions with rationale in `adr/`.

## Primary Documents

- Start with [`project/overview.md`](project/overview.md) for product intent and current repository context.
- Use [`project/requirements.md`](project/requirements.md) as the canonical MVP specification.
- Use [`project/architecture.md`](project/architecture.md) for target system structure and operational constraints.
- Use [`adr/README.md`](adr/README.md) for durable architecture and process decisions.

## Writing Guidelines

- Keep technical documentation in English.
- Avoid duplicating the same fact across multiple files.
- Prefer links to canonical documents over copy-pasting content.
- Update [`../README.md`](../README.md) only with high-level repository information; keep detailed internal context here.
