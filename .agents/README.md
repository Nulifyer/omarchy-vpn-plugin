# Agent work state

Read the repository-root `AGENTS.md` first, then use this order:

1. `PLAN.md` for the agreed goal, scope, boundaries, and phases.
2. `DECISIONS.md` for binding choices and unresolved questions.
3. `STATUS.md` for current project state, current batch, and the next action.
4. `TESTING.md` for commands and evidence standards.

## Maintenance rules

- Keep these files short and current. Git owns history.
- Replace stale status. Do not append a chronological diary.
- Put choices future work must preserve in `DECISIONS.md`, never task completion.
- Put stable discoveries and facts under the repository's documentation convention, usually `docs/`.
- Keep exact run results in contracts or evidence artifacts, not `STATUS.md` or `TESTING.md`.
- Preserve user-added sections and notes.
- Resolve every continuity validation error before another batch.

## Delivery loop

When autonomous commits are authorized: address one logical result, update its owning records, validate and test it, review and stage only that batch, commit it, then repeat from the single next action.
