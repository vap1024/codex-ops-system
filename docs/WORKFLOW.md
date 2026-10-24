# Source-checked workflow

The method is **Codex as an independent auditor**: freeze the brief, check
claims against primary sources, request a correction, and compare the delivered
files with the reviewed revision before owner acceptance.

## OPS-001: preserving a pending decision

This is an actual local review and correction made on 2026-10-24. The author
delegated implementation and checks to Codex. Implementation, source review,
and correction were separate passes in the same session. A second independently
operating auditor did not participate, and the author's final acceptance has
not been recorded. The protocol's full separation of roles is the target for
subsequent operations, not a participation claim about this example.

### 1. Freeze an observable brief

[BRIEF-OPS-001](audit/BRIEF-OPS-001.md), revision 1, was committed with its
[synthetic fixture](audit/fixtures/nested-heading.md) and regression test in
commit `b82e957`. The brief requires two requests in order, retained indented
evidence, a working section boundary, and no regressions in the existing suite.

The relevant fixture contains:

```markdown
## Waiting for decision
- Preserve the evidence for the first request.
  ## Evidence
  Demo data: synthetic fixtures
  This indented heading belongs to the first decision.
  - Compare the compact and detailed layouts.
- Keep the second request in the package.
```

### 2. Review the primary source and reproduce the finding

The review read `src/ops/_goals.py` and the fixture on disk. Section-heading
detection ran before list-continuation handling. The indented evidence heading
therefore ended the pending section; the second request was silently omitted.

The command actually run before changing the parser was:

```sh
python -m pytest -q tests/test_package.py::test_indented_heading_remains_inside_decision --tb=short
```

The [saved original output](audit/OPS-001-before.txt) records the failed
run: `AssertionError: assert 1 == 2`, followed by `1 failed` (exit code 1).
The brief and failing regression can be reproduced from commit `b82e957` in
a separate checkout with the development dependency installed. A later commit
stores the log; it does not pretend the original revision passed.

### 3. Make the scoped correction

Commit `ddee81c` changes `src/ops/_goals.py`: while a decision item is active,
an indented line is retained before testing for a new section heading.
Unindented major headings still end the section. The same regression command
then produced [the saved result](audit/OPS-001-after.txt): `1 passed` and exit
code 0. The commit also retains both real command outputs.

Inspect the correction without relying on this narrative:

```sh
git show ddee81c -- src/ops/_goals.py
```

### 4. Verify against files on disk

The complete test run after the correction and synthetic-label changes was
`python -m pytest`: **53 passed** on Python 3.13.15 with pytest 9.1.1.
`python examples/run_demo.py --output-dir examples/output` then generated the
two committed reports. Both contain `Demo data: synthetic fixtures`.

| Frozen criterion | Primary file or command | Observed technical result |
| --- | --- | --- |
| Two requests retained in source order | Regression test and `nested-heading.md` | Passed after the fix; failed before it |
| Nested evidence retained | Regression assertions against the first item's text | Passed |
| Major heading still ends the section | Existing section-boundary tests | Passed |
| Existing behavior still works | Complete pytest suite | 53 passed |
| Demo queue is reproducible | `examples/output/DECISION-PACKAGE.md` | Three requests, numbered 1 through 3 |
| Stale and boundary cases differ | `examples/output/STALE-GOALS.md` and goal headers | 53-day-old goal flagged; 14-day-old goal fresh |

The current technical criteria pass. **Final owner acceptance is pending.**
Neither a passing run nor this document stands in for an acceptor's decision.
The acceptor uses `templates/acceptance-checklist.md`, compares the delivered
revision with these files, reruns required commands, and records the outcome.
Any later source change requires review of the affected claims.

### 5. Keep requests separate from acceptance

The demo goals remain pending fictional requests. The builder collects them
without modifying sources or granting approval. Record a resolved request in
the goal's decision log before removing it from the waiting section. Rebuild
the package after decisions; keep old snapshots outside the goal folder.

## Application review contracts

The following sections give the two application repositories a stable place
to link their review cases. They are review contracts, not claims that this
session ran either application's implementation or accepted its results.

### l2-project-audit

Primary evidence: the synthetic announcement text, token-fate fields, metric
snapshot, component code, and generated audit report in that repository.
Reproduce both migration branches: full replacement and redirect. Check that
maintenance remains INFO and a critical announcement cannot produce a healthy
verdict. The application's own audit trail must name its actual finding, fix,
and command results. This flagship supplies the role and acceptance protocol.

### nft-collection-audit

Primary evidence: collection feature fixtures, scoring components, gate
threshold, time/price observations, and generated scorecards in that repository.
Check empty floor data against large volume claims, the 7.0 gate boundary,
and tracker observations against the mint baseline. The application's own
audit trail must supply a reproduced finding and correction. The model's
research disclaimer belongs beside its scores. No application score is
verified merely by being mentioned here.
