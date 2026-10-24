# Frozen brief: OPS-001

- Revision: 1
- Frozen on: 2026-10-24
- Scope: preserve indented Markdown headings inside pending decision items.
- Primary fixture: `docs/audit/fixtures/nested-heading.md`.
- Executor: the implementation pass in this Codex session.
- Reviewer: the subsequent source-review pass in the same Codex session.
- Acceptor: the project owner; final owner acceptance is pending.

## Acceptance criteria

1. The fixture yields exactly two pending decisions in source order.
2. The first decision retains its indented evidence heading and explanation.
3. The second decision is not dropped after the nested heading.
4. An unindented major heading still ends the pending-decision section.
5. The existing parser and stale-goal test suite remains green.

## Evidence to retain

Save the regression command and actual failing output before changing the
parser. Commit the regression separately from its fix, then rerun the same
command and the complete suite. Record concrete files, commits, and outcomes
in `docs/WORKFLOW.md`. The review is a real source review in this session;
it does not establish that a separately operating auditor participated.

The public Git revision of this brief is the frozen reference. A change to
these criteria requires a new explicit revision rather than editing history.
