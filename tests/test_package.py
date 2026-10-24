import os
from pathlib import Path
import re
import subprocess
import sys

import pytest

from ops._goals import GoalFormatError
from ops.package import build_package, collect_decisions


ROOT = Path(__file__).resolve().parents[1]


def test_demo_package_has_three_ordered_items(demo_goals, tmp_path, as_of):
    output = tmp_path / "DECISION-PACKAGE.md"
    result = build_package(demo_goals, output, as_of=as_of)
    content = output.read_text(encoding="utf-8")
    assert result.path == output.resolve()
    assert result.goal_count == 3
    assert len(result.items) == 3
    assert re.findall(r"^(\d+)\. \*\*", content, re.MULTILINE) == ["1", "2", "3"]
    assert [item.text.splitlines()[0] for item in result.items] == [
        "Choose the compact layout for the fictional notebook handoff.",
        "Approve a 14-day review interval for the fictional checklist.",
        "Assign the synthetic Role B as the acceptance reviewer.",
    ]
    assert {item.goal_id for item in result.items} == {"G-201"}
    source_lines = (demo_goals / "01-notebook-review.md").read_text().splitlines()
    for item in result.items:
        assert source_lines[item.line - 1] == "- " + item.text.splitlines()[0]
        assert f"Source: `{item.source}:{item.line}`" in content
    assert "G-202" not in content
    assert "G-203" not in content


def test_numbering_is_global_and_filenames_are_sorted(goal_factory, tmp_path, as_of):
    last = goal_factory("Z-last.md", goal_id="G-Z", body="## Waiting for decision\n9. Last.\n")
    goal_factory("a-first.md", goal_id="G-A", body="## Waiting for decision\n* First.\n+ Second.\n")
    (last.parent / "ignored.txt").write_text("not a goal", encoding="utf-8")
    nested = last.parent / "nested"
    nested.mkdir()
    (nested / "not-scanned.md").write_text("not a goal", encoding="utf-8")
    result = build_package(last.parent, tmp_path / "report.md", as_of=as_of)
    assert [item.text for item in result.items] == ["First.", "Second.", "Last."]
    assert [item.goal_id for item in result.items] == ["G-A", "G-A", "G-Z"]
    assert result.goal_count == 2
    assert re.findall(r"^(\d+)\. \*\*", result.path.read_text(), re.MULTILINE) == ["1", "2", "3"]
    assert collect_decisions(last.parent) == result.items


@pytest.mark.parametrize("body", [
    "## Status\nNo decisions.\n",
    "## Waiting for decision\n\n## Status\nCurrent.\n",
    "## Waiting for decisions\n- Different heading.\n",
    "## Notes\n```markdown\n## Waiting for decision\n- Only an example.\n```\n",
])
def test_absent_empty_or_example_section_contributes_no_items(goal_factory, body):
    goal = goal_factory(body=body)
    assert collect_decisions(goal.parent) == ()


def test_nested_items_and_continuations_stay_with_parent(goal_factory):
    goal = goal_factory(body=(
        "## Waiting for decision\n"
        "- Choose a layout.\n"
        "  Evidence: synthetic local draft.\n"
        "  - Compact option.\n"
        "  - Detailed option.\n\n"
        "2) Choose a reviewer.\n"
    ))
    items = collect_decisions(goal.parent)
    assert len(items) == 2
    assert items[0].text == (
        "Choose a layout.\n  Evidence: synthetic local draft.\n"
        "  - Compact option.\n  - Detailed option."
    )
    assert items[1].text == "Choose a reviewer."


def test_fenced_headings_and_bullets_are_not_parsed(goal_factory):
    goal = goal_factory(body=(
        "~~~markdown\n## Waiting for decision\n- Example only.\n~~~\n"
        "## Waiting for decision\n"
        "```text\n- Standalone example only.\n```\n"
        "- Keep the example attached.\n"
        "  ```markdown\n  ## Other heading\n  - Nested example only.\n  ```\n"
        "- Real second item.\n"
    ))
    items = collect_decisions(goal.parent)
    assert len(items) == 2
    assert "## Other heading" in items[0].text
    assert "Nested example only." in items[0].text
    assert items[1].text == "Real second item."


@pytest.mark.parametrize("heading", ["# Appendix", "## Decision log"])
def test_decision_section_ends_at_next_major_heading(goal_factory, heading):
    goal = goal_factory(body=f"## Waiting for decision\n- Pending.\n{heading}\n- Resolved.\n")
    assert [item.text for item in collect_decisions(goal.parent)] == ["Pending."]


def test_optional_closing_hashes_and_bom_are_supported(goal_factory):
    goal = goal_factory(name="example.MD", body="## Waiting for decision ##\n- Example choice.\n")
    goal.write_text(goal.read_text(), encoding="utf-8-sig")
    assert [item.text for item in collect_decisions(goal.parent)] == ["Example choice."]


@pytest.mark.parametrize("old,new", [
    ("---\nid:", "id:"),
    ("updated: 2026-10-24\n---", "updated: 2026-10-24"),
    ("id: G-EXAMPLE", "id: lowercase"),
    ("id: G-EXAMPLE", "id: G-EXAMPLE\nid: G-OTHER"),
    ("updated: 2026-10-24", "updated: 2026-02-30"),
    ("updated: 2026-10-24", "updated: 20261024"),
    ("updated: 2026-10-24", "state: active"),
    ("# Example goal", "## Example goal"),
])
def test_invalid_headers_fail_without_replacing_existing_report(
    goal_factory, tmp_path, old, new,
):
    goal = goal_factory()
    goal.write_text(goal.read_text().replace(old, new), encoding="utf-8")
    output = tmp_path / "report.md"
    output.write_text("previous accepted snapshot", encoding="utf-8")
    with pytest.raises(GoalFormatError):
        build_package(goal.parent, output)
    assert output.read_text() == "previous accepted snapshot"


@pytest.mark.parametrize("body", [
    "## Waiting for decision\nA request without a list marker.\n",
    "## Waiting for decision\n-   \n",
    "## Waiting for decision\n- A.\n## Waiting for decision\n- B.\n",
    "## Notes\n```markdown\n## Waiting for decision\n- Unclosed example.\n",
])
def test_malformed_decision_sections_raise_actionable_errors(goal_factory, body):
    goal = goal_factory(body=body)
    with pytest.raises(GoalFormatError, match=r"example\.md"):
        collect_decisions(goal.parent)


def test_duplicate_ids_fail(goal_factory):
    first = goal_factory("a.md")
    goal_factory("b.md")
    with pytest.raises(GoalFormatError, match="unique"):
        collect_decisions(first.parent)


def test_empty_folder_produces_explicit_empty_report(tmp_path, as_of):
    goals = tmp_path / "goals"
    goals.mkdir()
    result = build_package(goals, tmp_path / "report.md", as_of=as_of)
    assert result.items == ()
    assert result.goal_count == 0
    assert "No decisions waiting." in result.path.read_text()


def test_missing_folder_is_an_error(tmp_path):
    with pytest.raises(ValueError, match="does not exist"):
        collect_decisions(tmp_path / "missing")


@pytest.mark.parametrize("name", ["example.md", "nested/report.md"])
def test_output_cannot_overwrite_a_goal_or_enter_input_folder(goal_factory, name):
    goal = goal_factory()
    before = goal.read_bytes()
    with pytest.raises(ValueError, match="outside"):
        build_package(goal.parent, goal.parent / name)
    assert goal.read_bytes() == before
    assert not (goal.parent / "nested").exists()


def test_report_is_deterministic_and_goals_are_unchanged(demo_goals, tmp_path, as_of):
    before = {path.name: path.read_bytes() for path in demo_goals.iterdir()}
    first = build_package(demo_goals, tmp_path / "one.md", as_of=as_of)
    second = build_package(demo_goals, tmp_path / "two.md", as_of=as_of)
    assert first.path.read_bytes() == second.path.read_bytes()
    assert {path.name: path.read_bytes() for path in demo_goals.iterdir()} == before


def test_demo_runs_from_another_working_directory(tmp_path):
    run = subprocess.run(
        [sys.executable, str(ROOT / "examples" / "run_demo.py")],
        cwd=tmp_path, capture_output=True, text=True, check=True,
    )
    assert "Goals scanned: 3" in run.stdout
    assert "Decision items: 3" in run.stdout
    assert "Stale goals: 1" in run.stdout
    paths = [Path(line.split(": ", 1)[1]) for line in run.stdout.splitlines()
             if line.startswith(("Decision package: ", "Stale report: "))]
    assert len(paths) == 2
    assert all(path.is_file() for path in paths)
    assert paths[0].parent == paths[1].parent
    # The public demo retains its reports. This test removes only its own run.
    for path in paths:
        path.unlink()
    paths[0].parent.rmdir()


def test_demo_accepts_explicit_output_directory(tmp_path):
    output = tmp_path / "reports"
    run = subprocess.run(
        [sys.executable, str(ROOT / "examples" / "run_demo.py"), "--output-dir", str(output)],
        cwd=tmp_path, capture_output=True, text=True, check=True,
    )
    assert str((output / "DECISION-PACKAGE.md").resolve()) in run.stdout
    assert "Decision items: 3" in (output / "DECISION-PACKAGE.md").read_text()
    assert "Stale goals: 1" in (output / "STALE-GOALS.md").read_text()


@pytest.mark.parametrize("module", ["ops.package", "ops.stale"])
def test_module_cli_writes_report_and_handles_invalid_input(module, tmp_path, demo_goals):
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    output = tmp_path / "report.md"
    command = [sys.executable, "-m", module, str(demo_goals), "--output", str(output),
               "--as-of", "2026-10-24"]
    run = subprocess.run(command, env=env, capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    content = output.read_text()
    assert ("Decision items: 3" if module == "ops.package" else "Stale goals: 1") in content
    failed = subprocess.run(
        [sys.executable, "-m", module, str(tmp_path / "missing")],
        env=env, capture_output=True, text=True,
    )
    assert failed.returncode == 2
    assert "error:" in failed.stderr
    assert "Traceback" not in failed.stderr
