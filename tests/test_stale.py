from datetime import timedelta
import os

import pytest

from ops._goals import GoalFormatError
from ops.stale import find_stale_goals, main, write_stale_report


def test_demo_marks_only_the_old_goal(demo_goals, as_of):
    stale = find_stale_goals(demo_goals, days=14, as_of=as_of)
    assert len(stale) == 1
    assert stale[0].goal_id == "G-202"
    assert stale[0].source == "02-archive-review.md"
    assert stale[0].age_days == 53
    assert stale[0].updated.isoformat() == "2026-09-01"


@pytest.mark.parametrize("age,is_stale", [(0, False), (13, False), (14, False), (15, True), (50, True)])
def test_stale_threshold_is_strict(goal_factory, as_of, age, is_stale):
    goal = goal_factory(updated=(as_of - timedelta(days=age)).isoformat())
    stale = find_stale_goals(goal.parent, days=14, as_of=as_of)
    assert bool(stale) is is_stale
    if is_stale:
        assert stale[0].age_days == age


def test_zero_day_threshold_flags_yesterday_but_not_today(goal_factory, as_of):
    today = goal_factory("today.md", goal_id="G-TODAY", updated=as_of.isoformat())
    goal_factory("yesterday.md", goal_id="G-YESTERDAY", updated=(as_of - timedelta(days=1)).isoformat())
    assert [g.goal_id for g in find_stale_goals(today.parent, days=0, as_of=as_of)] == ["G-YESTERDAY"]


def test_negative_threshold_fails_without_replacing_report(goal_factory, tmp_path, as_of):
    goal = goal_factory()
    output = tmp_path / "report.md"
    output.write_text("earlier snapshot", encoding="utf-8")
    with pytest.raises(ValueError, match="non-negative"):
        write_stale_report(goal.parent, output, days=-1, as_of=as_of)
    assert output.read_text() == "earlier snapshot"


def test_future_header_date_is_rejected(goal_factory, as_of):
    goal = goal_factory(updated=(as_of + timedelta(days=1)).isoformat())
    with pytest.raises(ValueError, match="after the report date"):
        find_stale_goals(goal.parent, as_of=as_of)


def test_filesystem_timestamp_does_not_determine_age(goal_factory, as_of):
    old = goal_factory("old.md", goal_id="G-OLD", updated="2026-09-01")
    fresh = goal_factory("fresh.md", goal_id="G-FRESH", updated=as_of.isoformat())
    os.utime(old, (1800000000, 1800000000))
    os.utime(fresh, (0, 0))
    assert [g.goal_id for g in find_stale_goals(old.parent, as_of=as_of)] == ["G-OLD"]


def test_missing_update_date_is_not_silently_skipped(goal_factory, as_of):
    goal = goal_factory()
    goal.write_text(goal.read_text().replace("updated: 2026-10-24\n", ""), encoding="utf-8")
    with pytest.raises(GoalFormatError, match="updated"):
        find_stale_goals(goal.parent, as_of=as_of)


def test_stale_report_has_date_threshold_and_source(demo_goals, tmp_path, as_of):
    output = tmp_path / "nested" / "STALE-GOALS.md"
    before = {p.name: p.read_bytes() for p in demo_goals.iterdir()}
    stale = write_stale_report(demo_goals, output, as_of=as_of)
    content = output.read_text()
    assert "As of: 2026-10-24" in content
    assert "Threshold: strictly more than 14 days" in content
    assert "Stale goals: 1" in content
    assert "53 days old" in content
    assert "02-archive-review.md" in content
    assert stale == find_stale_goals(demo_goals, as_of=as_of)
    assert {p.name: p.read_bytes() for p in demo_goals.iterdir()} == before


def test_empty_stale_report(goal_factory, tmp_path, as_of):
    goal = goal_factory(updated=as_of.isoformat())
    output = tmp_path / "report.md"
    assert write_stale_report(goal.parent, output, as_of=as_of) == ()
    assert "No stale goals." in output.read_text()


def test_stale_report_cannot_modify_source_goal(goal_factory, as_of):
    goal = goal_factory()
    before = goal.read_bytes()
    with pytest.raises(ValueError, match="outside"):
        write_stale_report(goal.parent, goal, as_of=as_of)
    assert goal.read_bytes() == before


@pytest.mark.parametrize("date_text", ["20261024", "2026-02-30", "example"])
def test_cli_rejects_invalid_reference_dates(demo_goals, date_text, capsys):
    with pytest.raises(SystemExit) as error:
        main([str(demo_goals), "--as-of", date_text])
    assert error.value.code == 2
    assert "error:" in capsys.readouterr().err
