"""Build two reproducible reports from the bundled synthetic goals."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ops.package import build_package  # noqa: E402
from ops.stale import write_stale_report  # noqa: E402


DEMO_DATE = date(2026, 10, 24)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, help="default: a new OS temporary folder")
    args = parser.parse_args(argv)
    output = args.output_dir if args.output_dir is not None else Path(
        tempfile.mkdtemp(prefix="codex-ops-")
    )
    goals = ROOT / "data" / "goals"
    try:
        package = build_package(
            goals, output / "DECISION-PACKAGE.md", as_of=DEMO_DATE, synthetic=True,
        )
        stale_path = output / "STALE-GOALS.md"
        stale = write_stale_report(goals, stale_path, days=14, as_of=DEMO_DATE, synthetic=True)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")
    print("Demo data: synthetic fixtures")
    print(f"Reference date: {DEMO_DATE.isoformat()} | threshold 14 days")
    print(f"Goals scanned: {package.goal_count}")
    print(f"Decision items: {len(package.items)}")
    print(f"Stale goals: {len(stale)}")
    print(f"Decision package: {package.path}")
    print(f"Stale report: {stale_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
