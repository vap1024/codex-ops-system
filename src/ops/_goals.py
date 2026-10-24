"""The intentionally small Markdown format shared by both report commands."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import os
from pathlib import Path
import re
import tempfile


class GoalFormatError(ValueError):
    """A source goal does not follow the documented format."""


@dataclass(frozen=True)
class Goal:
    path: Path
    goal_id: str
    title: str
    updated: date
    decisions: tuple[tuple[str, int], ...]


_HEADING = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.+?)(?:[ \t]+#+)?[ \t]*$")
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
_ITEM = re.compile(r"^(?:[-+*]|[0-9]+[.)])[ \t]+(.*)$")


def iso_date(value: str) -> date:
    """Accept only the portable YYYY-MM-DD spelling."""
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError("expected a date in YYYY-MM-DD format")
    return date.fromisoformat(value)


def _decisions(lines: list[str], start: int, path: Path) -> tuple[tuple[str, int], ...]:
    items: list[tuple[str, int]] = []
    current: list[str] = []
    current_line = 0
    active = False
    seen = False
    fence: str | None = None

    def finish() -> None:
        if current:
            body = "\n".join(current).rstrip()
            if not body.strip():
                raise GoalFormatError(f"{path.name}:{current_line}: empty decision item")
            items.append((body, current_line))
            current.clear()

    for index in range(start, len(lines)):
        line = lines[index]
        marker = _FENCE.match(line)
        if fence is not None:
            if active and current:
                current.append(line)
            if (marker and marker[1][0] == fence[0]
                    and len(marker[1]) >= len(fence) and not marker[2].strip()):
                fence = None
            continue
        if marker:
            fence = marker[1]
            if active and current:
                current.append(line)
            continue

        # An indented heading is part of the current list item. Check list
        # continuation before looking for a new top-level section.
        if active and current and line.startswith((" ", "\t")):
            current.append(line)
            continue

        heading = _HEADING.match(line)
        if heading and len(heading[1]) <= 2:
            finish()
            active = False
            if len(heading[1]) == 2 and heading[2] == "Waiting for decision":
                if seen:
                    raise GoalFormatError(f"{path.name}:{index + 1}: duplicate decision section")
                seen = active = True
            continue
        if not active:
            continue
        item = _ITEM.match(line)
        if item:
            finish()
            current = [item[1]]
            current_line = index + 1
        elif not line.strip():
            if current:
                current.append("")
        else:
            raise GoalFormatError(
                f"{path.name}:{index + 1}: decisions must be top-level list items; "
                "indent continuation lines"
            )
    if fence is not None:
        raise GoalFormatError(f"{path.name}: unclosed fenced block")
    finish()
    return tuple(items)


def read_goal(path: Path) -> Goal:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    if not lines or lines[0] != "---":
        raise GoalFormatError(f"{path.name}: missing metadata header")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise GoalFormatError(f"{path.name}: unclosed metadata header") from exc
    fields: dict[str, str] = {}
    for line in lines[1:end]:
        key, sep, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if not sep or not key or not value or key in fields:
            raise GoalFormatError(f"{path.name}: invalid or duplicate metadata field")
        fields[key] = value
    goal_id = fields.get("id", "")
    if not re.fullmatch(r"[A-Z][A-Z0-9_-]{0,31}", goal_id):
        raise GoalFormatError(f"{path.name}: id must be 1-32 uppercase letters, digits, _ or -")
    try:
        updated = iso_date(fields.get("updated", ""))
    except ValueError as exc:
        raise GoalFormatError(f"{path.name}: invalid updated date: {exc}") from exc
    title_line = next((i for i in range(end + 1, len(lines)) if lines[i].strip()), None)
    title = _HEADING.match(lines[title_line]) if title_line is not None else None
    if not title or len(title[1]) != 1:
        raise GoalFormatError(f"{path.name}: metadata must be followed by a # Title")
    return Goal(path, goal_id, title[2], updated, _decisions(lines, title_line + 1, path))


def read_goals(folder: str | Path) -> tuple[Goal, ...]:
    root = Path(folder)
    if not root.is_dir():
        raise ValueError(f"goal folder does not exist: {root}")
    paths = sorted(
        (p for p in root.iterdir() if p.is_file() and p.suffix.lower() == ".md"),
        key=lambda p: (p.name.casefold(), p.name),
    )
    goals = tuple(read_goal(path) for path in paths)
    identifiers = [goal.goal_id for goal in goals]
    if len(set(identifiers)) != len(identifiers):
        raise GoalFormatError("goal ids must be unique within the folder")
    return goals


def write_report(folder: str | Path, output: str | Path, content: str) -> Path:
    """Keep source folders immutable and replace reports atomically."""
    destination = Path(output).resolve()
    if destination.is_relative_to(Path(folder).resolve()):
        raise ValueError("report output must be outside the goal folder")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=destination.parent,
            prefix=f".{destination.name}.", suffix=".tmp", delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        os.replace(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return destination
