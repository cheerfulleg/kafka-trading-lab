# Repository instructions

## Purpose

This is a learning and portfolio project for production-grade Kafka patterns in
a trading domain. Prefer changes that demonstrate correctness, failure
handling, observability, schema evolution, or explicit engineering trade-offs.

## Daily agent contract

1. Read `README.md`, `BACKLOG.md`, and relevant code before editing.
2. Select exactly one unchecked item from the first non-empty backlog section.
3. Keep the change small enough for one focused pull request.
4. Implement production-quality code, tests, and concise documentation.
5. Mark the selected backlog item complete only when its acceptance criteria
   are satisfied.
6. Run all quality gates before finishing.
7. If the task is ambiguous or unsafe, make no code change and explain why.

## Non-negotiable guardrails

- Never edit files under `.github/` or `automation/`.
- Never edit `AGENTS.md` or weaken test, lint, typing, or security checks.
- Never add secrets, credentials, tokens, generated activity, or empty commits.
- Never push, create or merge a PR, or change repository settings. The local
  wrapper owns branch publication after verification.
- Never add a dependency without explaining why in the PR summary.
- Never fabricate benchmark numbers or claim a test was run when it was not.
- Do not refactor unrelated code.

## Engineering conventions

- Python 3.12+, full type annotations, Pydantic v2.
- Use UTC-aware datetimes at all boundaries.
- Treat event schemas as public contracts.
- Prefer deterministic unit tests; integration tests must be explicitly marked.
- Log identifiers and outcomes, never entire sensitive payloads.
- Preserve backward compatibility unless the backlog item explicitly studies a
  breaking change.

## Quality gates

```bash
ruff check .
ruff format --check .
mypy src
pytest
```

The pull request summary must include:

- backlog item selected;
- implementation and design choices;
- tests actually executed;
- risks, limitations, and a reasonable next step.
