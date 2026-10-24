# codex-ops-system

Frozen briefs, source-checked reviews, and daily decision packages for Codex as an independent auditor.

[![CI](https://github.com/vap1024/codex-ops-system/actions/workflows/tests.yml/badge.svg)](https://github.com/vap1024/codex-ops-system/actions/workflows/tests.yml)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Open-source edition of a toolkit I use in my own operation; all demo data is synthetic.

## What it does

- Freezes the task brief before an executor starts work.
- Separates executor claims, Codex source checks, and the owner's acceptance.
- Collects pending choices from goal files into one consecutively numbered package.
- Flags goals older than a review threshold using header dates, with a strict boundary.
- Preserves source lines, nested evidence, and synthetic labels in reproducible demo reports.

## Sample output

Generated files: [DECISION-PACKAGE.md](examples/output/DECISION-PACKAGE.md)
and [STALE-GOALS.md](examples/output/STALE-GOALS.md).

```text
Demo data: synthetic fixtures
As of: 2026-10-24
Goals scanned: 3
Decision items: 3
Stale goals: 1
```

The oldest goal is 53 days old. A second goal is exactly 14 days old and stays
fresh at a 14-day threshold. These are synthetic review cases, not operational
claims about real projects.

## Audit trail

**OPS-001:** the [frozen brief](docs/audit/BRIEF-OPS-001.md) required two pending
requests and preserved nested evidence. Source review found that an indented
`## Evidence` heading ended the decision section: the
[regression actually failed](docs/audit/OPS-001-before.txt), returning one
request instead of two. The fix checks list continuation before section
headings; the [same test then passed](docs/audit/OPS-001-after.txt).

See [the complete workflow and commit references](docs/WORKFLOW.md#ops-001-preserving-a-pending-decision).
Implementation and review occurred in separate passes of this Codex session.
No separately operating auditor or final owner acceptance is claimed.

## Quickstart

Python **3.11+** and Git are required. From an empty working directory:

```sh
git clone https://github.com/vap1024/codex-ops-system.git
python -m pip install -r codex-ops-system/requirements.txt
python codex-ops-system/examples/run_demo.py
```

The hosted clone is a publication target for **2026-10-27**. Until publication,
use the delivered local repository; a fresh local Git clone was verified.
GitHub CI, release, and hosted cross-links remain pending publication.

The demo prints paths to two reports retained in a new OS temporary folder
(`/tmp` on Linux, `%TEMP%` on Windows). It fixes the reference date at 2026-10-24
and the threshold at 14 days. To regenerate the committed samples from the
repository root, run `python examples/run_demo.py --output-dir examples/output`.
The demo uses only the standard library and makes no external requests.

## Tests

From the repository root, after installing `requirements.txt`:

```sh
python -m pytest
```

Actual local result: **53 passed** on Python 3.13.15 with pytest 9.1.1.
The suite covers numbering, empty and absent sections, nested headings and
fences, invalid metadata, unchanged sources, synthetic labeling, CLI behavior,
and stale-date boundaries. The single CI job targets Ubuntu and Python 3.11;
no hosted CI result is claimed before it runs.

## How Codex is used

I set tasks for agents and accept their results by checking the delivered files;
I do not hand-write the implementation. The method uses **Codex as an independent
auditor**: read the frozen brief and primary files, reproduce material checks,
record findings, and return evidence to a separate acceptor. A summary alone
cannot establish completion. The author compares the audited version with disk
before accepting it. This project is built with Codex; its public OPS-001 record
states exactly which review roles were exercised in this session.

## Cross-links

Part of a Codex-auditor toolchain:

| Repository | Task | What it teaches |
| --- | --- | --- |
| [l2-project-audit](https://github.com/vap1024/l2-project-audit) | Announcement risk, token fate, and project health | Check a risk verdict against announcements and metric snapshots. |
| [nft-collection-audit](https://github.com/vap1024/nft-collection-audit) | Pre-mint collection scoring and price observations | Check component evidence and gate boundaries before accepting a score. |

The flagship supplies the [shared protocol](docs/PROTOCOL.md) and
[worked audit trail](docs/WORKFLOW.md); the other repositories apply the method.
Their linked implementations and hosted availability are verified in their own
reviews, not inferred from this table.

## Structure

```text
.github/workflows/   One Ubuntu / Python 3.11 test job
docs/               Protocol, actual workflow, goal format, primary audit evidence
templates/          Audit brief, acceptance checklist, goal, decision item
src/ops/            Goal reader, decision package builder, stale detector
data/goals/         Three synthetic goals, including stale and boundary cases
examples/output/    Actual generated and labeled reports
tests/              Pytest suite
CHANGELOG.md        v0.1.0 scope and limitations
```

See [GOAL-FORMAT.md](docs/GOAL-FORMAT.md) for the input contract, CLI commands,
output guarantees, and error handling. Runtime dependencies: standard library
only. Development dependency: the exact pytest version in `requirements.txt`.
The tool assembles reports; decisions and acceptance remain human records.

## License

[MIT](LICENSE).
