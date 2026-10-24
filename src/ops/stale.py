"""Report goals whose updated date is strictly older than the threshold."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from ._goals import iso_date, read_goals, write_report


@dataclass(frozen=True)
class StaleGoal:
    goal_id: str
    title: str
    source: str
    updated: date
    age_days: int


def find_stale_goals(
    folder: str | Path, *, days: int = 14, as_of: date | None = None,
) -> tuple[StaleGoal, ...]:
    """Compare header dates, never filesystem modification times."""
    if days < 0:
        raise ValueError("days must be non-negative")
    report_date = as_of if as_of is not None else date.today()
    stale: list[StaleGoal] = []
    for goal in read_goals(folder):
        age = (report_date - goal.updated).days
        if age < 0:
            raise ValueError(f"{goal.path.name}: updated date is after the report date")
        if age > days:
            stale.append(StaleGoal(goal.goal_id, goal.title, goal.path.name, goal.updated, age))
    return tuple(stale)


def write_stale_report(
    folder: str | Path, output: str | Path, *, days: int = 14, as_of: date | None = None,
    synthetic: bool = False,
) -> tuple[StaleGoal, ...]:
    report_date = as_of if as_of is not None else date.today()
    stale = find_stale_goals(folder, days=days, as_of=report_date)
    lines = [
        "# Stale goal report", "",
    ]
    if synthetic:
        lines += ["Demo data: synthetic fixtures", ""]
    lines += [
        f"As of: {report_date.isoformat()}",
        f"Threshold: strictly more than {days} days", f"Stale goals: {len(stale)}", "",
    ]
    if not stale:
        lines += ["No stale goals.", ""]
    for goal in stale:
        lines += [
            f"- **{goal.goal_id} | {goal.title}**: updated {goal.updated.isoformat()}, "
            f"{goal.age_days} days old. Source: `{goal.source}`.", "",
        ]
    write_report(folder, output, "\n".join(lines))
    return stale


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("goals", type=Path, help="flat folder containing goal Markdown")
    parser.add_argument("--days", type=int, default=14)
    parser.add_argument("--as-of", type=iso_date, default=None, metavar="YYYY-MM-DD")
    parser.add_argument("--output", type=Path, default=Path("STALE-GOALS.md"))
    parser.add_argument("--synthetic", action="store_true", help="label a synthetic demonstration")
    args = parser.parse_args(argv)
    try:
        stale = write_stale_report(
            args.goals, args.output, days=args.days, as_of=args.as_of, synthetic=args.synthetic,
        )
    except (OSError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")
    print(f"{len(stale)} stale goals -> {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
