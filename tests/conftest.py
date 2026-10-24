from datetime import date
from pathlib import Path

import pytest


@pytest.fixture
def demo_goals():
    return Path(__file__).resolve().parents[1] / "data" / "goals"


@pytest.fixture
def as_of():
    return date(2026, 10, 24)


@pytest.fixture
def goal_factory(tmp_path):
    folder = tmp_path / "goals"
    folder.mkdir()

    def create(
        name="example.md", *, goal_id="G-EXAMPLE", updated="2026-10-24",
        body="## Waiting for decision\n- Choose the example layout.\n",
    ):
        path = folder / name
        path.write_text(
            f"---\nid: {goal_id}\nupdated: {updated}\n---\n# Example goal\n\n{body}",
            encoding="utf-8",
        )
        return path

    return create
