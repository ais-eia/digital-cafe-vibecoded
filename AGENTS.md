# Digital Cafe Workflow

Every feature or change must follow this workflow in order:

1. **Study**: Analyze the request, current codebase, feasibility, approach, tradeoffs, risks, and verification strategy. Record the result in a new markdown file under `doc/study/`. Do not write implementation code before the study is complete.
2. **Plan**: Convert the study into a concrete, checkable implementation checklist in a new markdown file under `doc/plan/`.
3. **Execute plan**: Create a focused git branch, implement the checklist, and keep the checklist current as work progresses. Use Conventional Commits for all commits, such as `feat:`, `fix:`, `chore:`, `build:`, or `docs:`.
4. **Rendezvous**: Verify the branch, merge it into `main`, confirm the merged application works, and push the merged `main` branch to `origin`.
5. **Sync docs**: Update `doc/wiki/` to describe the current codebase, setup, behavior, and any operational notes after the merge.

## Repository Safety

- Never commit the virtual environment, local SQLite databases, credentials, API keys, or other sensitive settings.
- Keep changes scoped to the active feature or change.
- Run the relevant tests and application checks before the rendezvous step.
- Do not skip a workflow stage; if a stage cannot be completed, document the blocker before proceeding.
