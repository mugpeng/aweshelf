"""Session discovery commands."""

import json

import click

from aweshelf.lib.discovery import find_project_sessions


def format_sessions_json(sessions: list[dict]) -> str:
    return json.dumps(sessions, indent=2, ensure_ascii=False)


def format_sessions_table(sessions: list[dict]) -> str:
    if not sessions:
        return "No sessions found."
    headers = ["PROVIDER", "TITLE", "PROJECT", "SESSION"]
    rows = [
        [
            s.get("provider", "-"),
            _truncate(s.get("title", "Untitled session"), 48),
            _truncate(s.get("project_path", "-") or "-", 40),
            s.get("session_id", "-"),
        ]
        for s in sessions
    ]
    widths = [len(header) for header in headers]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))
    lines = [
        "  ".join(header.ljust(widths[index]) for index, header in enumerate(headers)),
        "  ".join("-" * width for width in widths),
    ]
    for row in rows:
        lines.append("  ".join(cell.ljust(widths[index]) for index, cell in enumerate(row)))
    return "\n".join(lines)


@click.command("sessions")
@click.option("-n", "--limit", default=20, type=int, help="Max sessions to show (0 = all).")
@click.option("--json", "as_json", is_flag=True, help="Output as raw JSON.")
def sessions_command(limit, as_json):
    """List discoverable sessions in the current project."""
    sessions = find_project_sessions()
    if limit > 0:
        sessions = sessions[:limit]
    click.echo(format_sessions_json(sessions) if as_json else format_sessions_table(sessions))


def _truncate(value: str, limit: int) -> str:
    return value[: limit - 3] + "..." if len(value) > limit else value
