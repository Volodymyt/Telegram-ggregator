# Roadmap

This document tracks near-term and mid-term delivery themes.

It must stay useful as the entry point for backlog decomposition, not only as a pointer to active documents.

## Horizon

Use milestone-oriented sections such as:

- `Now`
- `Next`
- `Later`

## Guidance

- Keep roadmap items outcome-oriented, not implementation-heavy.
- Link detailed execution work from [`active/`](active/README.md) when a roadmap item becomes active.
- Make sure each roadmap theme is still specific enough to decompose into milestones without reopening core technical decisions.
- Keep roadmap themes traceable to product requirements, acceptance criteria, and active delivery plans.
- Remove or rewrite stale themes rather than accumulating outdated plans.

## Now

- Make MVP delivery decomposition-ready by locking milestone sequencing, technical defaults, recovery semantics, and requirement coverage for the current implementation baseline. Detailed plan: [2026-03-14-mvp-delivery-plan.md](active/2026-03-14-mvp-delivery-plan.md).
- Execute the `M0 Foundations Ready` milestone to replace the legacy runtime baseline with the canonical package, config/login contract, storage foundation, storage readiness, and operability foundations. Active epic: [M0 Foundations Ready](active/01_0001_foundations_ready/0001_foundations_ready.md).
- Deliver the first executable MVP path through foundations, intake, candidate creation, event deduplication, and text publication with attribution. Detailed plan: [2026-03-14-mvp-delivery-plan.md](active/2026-03-14-mvp-delivery-plan.md).

## Next

- Complete the full event lifecycle, including `clear` handling, restart-safe recovery for candidate and publish states, and deterministic publish retry and failure handling. Promote this work only after the first end-to-end publish slice is stable. Detailed plan: [2026-03-14-mvp-delivery-plan.md](active/2026-03-14-mvp-delivery-plan.md).
- Raise the service to the documented MVP acceptance bar for media support, operability, capacity, latency, and container hardening on the target VPS profile. Promote this work after lifecycle recovery is in place. Detailed plan: [2026-03-14-mvp-delivery-plan.md](active/2026-03-14-mvp-delivery-plan.md).

## Later

- Convert validated MVP learnings into prioritized post-MVP backlog items without reopening accepted MVP architecture constraints or pulling out-of-scope features into the active stream too early. Backlog: [backlog.md](backlog.md).
