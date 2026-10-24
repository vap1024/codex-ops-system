"""Collect pending decisions into one numbered Markdown document."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from ._goals import iso_date, read_goals, write_report


@dataclass(frozen=True)
class DecisionItem:
    goal_id: str
    title: str
    source: str
    line: int
    text: str


@dataclass(frozen=True)
class PackageResult:
    path: Path
    goal_count: int
    items: tuple[DecisionItem, ...]


def collect_decisions(folder: str | Path) -> tuple[DecisionItem, ...]:
    """Read a flat goal folder in filename order, then preserve item order."""
    return tuple(
        DecisionItem(goal.goal_id, goal.title, goal.path.name, line, text)
        for goal in read_goals(folder)
        for text, line in goal.decisions
    )


def build_package(
    folder: str | Path, output: str | Path, *, as_of: date | None = None,
) -> PackageResult:
    """Validate every goal before replacing the output; never approve a request."""
    goals = read_goals(folder)
    items = tuple(
        DecisionItem(goal.goal_id, goal.title, goal.path.name, line, text)
        for goal in goals for text, line in goal.decisions
    )
    report_date = as_of if as_of is not None else date.today()
    lines = [
        "# Daily decision package", "", f"As of: {report_date.isoformat()}",
        f"Goals scanned: {len(goals)}", f"Decision items: {len(items)}", "",
        "These are pending requests. This package does not record approval or acceptance.", "",
    ]
    if not items:
        lines += ["No decisions waiting.", ""]
    for number, item in enumerate(items, 1):
        body = item.text.splitlines()
        lines.append(f"{number}. **{item.goal_id} | {item.title}** - {body[0]}")
        # Source continuations already have Markdown list indentation. Add one
        # ordered-list level so nested lists and fenced examples stay in this item.
        indent = " " * (len(str(number)) + 2)
        lines.extend(indent + line if line else "" for line in body[1:])
        lines += [f"{indent}Source: `{item.source}:{item.line}`", ""]
    path = write_report(folder, output, "\n".join(lines))
    return PackageResult(path, len(goals), items)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("goals", type=Path, help="flat folder containing goal Markdown")
    parser.add_argument("--output", type=Path, default=Path("DECISION-PACKAGE.md"))
    parser.add_argument("--as-of", type=iso_date, default=None, metavar="YYYY-MM-DD")
    args = parser.parse_args(argv)
    try:
        result = build_package(args.goals, args.output, as_of=args.as_of)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")
    print(f"{len(result.items)} decision items from {result.goal_count} goals -> {result.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
