# Goal format and report commands

## Header and folder

Each UTF-8 `.md` file begins with the following small metadata header and
a level-one title. A UTF-8 BOM is supported.

```markdown
---
id: G-EXAMPLE
updated: 2026-10-24
---
# Example goal

## Waiting for decision
- Choose a review layout.
  Options: compact or detailed.
```

This is a simple `key: value` format, not general YAML. `id` and `updated`
are required; duplicate or empty fields are errors. Additional nonempty
single-line fields are allowed. IDs are unique within the folder, start with
an uppercase letter, and use at most 32 uppercase letters, digits, `_` or `-`.
Dates use exactly `YYYY-MM-DD` and must be valid calendar dates.

Only immediate `.md` files are scanned, in filename order without regard to
letter case, with a spelling tie-break. Nested folders are not scanned.

## Pending items

The heading `## Waiting for decision` starts the section. Its top-level items
use `-`, `+`, `*`, `1.` or `1)`; the package assigns new consecutive numbers
across all goals. Indent continuation text and nested lists. Indented headings
inside an active item are retained. An unindented level-one or level-two
heading ends the section. Fenced examples are not interpreted as requests;
fenced evidence inside an item is retained.

Absent and empty decision sections contribute zero requests. Duplicate waiting
sections, empty list items, unindented prose inside the waiting section, and
unclosed fences are errors. The reader validates every goal before replacing
a report, including goals without decisions. This is a deliberately limited
Markdown contract, not a complete CommonMark parser.

## Commands

From the repository root, set the import path once for your shell:

```powershell
$env:PYTHONPATH = "src"
```

```sh
export PYTHONPATH=src
```

Then run:

```sh
python -m ops.package data/goals --output DECISION-PACKAGE.md --as-of 2026-10-24 --synthetic
python -m ops.stale data/goals --output STALE-GOALS.md --days 14 --as-of 2026-10-24 --synthetic
```

`--synthetic` labels a demo report explicitly. The bundled demo always enables
it. Ordinary local inputs are not automatically labeled as fictional.

Without `--as-of`, each command uses the machine's current local calendar date.
The demo fixes it at 2026-10-24. A goal is stale only when
`(as_of - updated).days > days`: 14 days is fresh at a threshold of 14.
Negative thresholds and future header dates are errors in the stale check.
Filesystem modification times do not determine age.

Reports must be outside the input folder. Output replacement is atomic on
success; sources remain unchanged. CLI input and I/O errors return exit code 2.
Finding stale goals is a successful report with exit code 0. The command-line
interface does not accept decisions, run agents, or schedule follow-up work.
