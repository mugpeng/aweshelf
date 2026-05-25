"""Session file discovery for Claude Code and Codex."""

import os
from pathlib import Path
from typing import Optional

from aweshelf.lib.session import parse_session_meta


CLAUDE_PROJECTS_DIR = Path("~/.claude/projects").expanduser()
CODEX_SESSIONS_DIR = Path("~/.codex/sessions").expanduser()


def find_claude_sessions() -> list[dict]:
    results = []
    if not CLAUDE_PROJECTS_DIR.exists():
        return results
    for jsonl_path in CLAUDE_PROJECTS_DIR.rglob("*.jsonl"):
        if "/subagents/" in str(jsonl_path):
            continue
        try:
            meta = parse_session_meta(jsonl_path)
            meta["source_path"] = str(jsonl_path)
            results.append(meta)
        except Exception:
            continue
    return results


def find_codex_sessions() -> list[dict]:
    results = []
    if not CODEX_SESSIONS_DIR.exists():
        return results
    for jsonl_path in CODEX_SESSIONS_DIR.rglob("*.jsonl"):
        try:
            meta = parse_session_meta(jsonl_path)
            meta["source_path"] = str(jsonl_path)
            results.append(meta)
        except Exception:
            continue
    return results


def find_all_sessions() -> list[dict]:
    return find_claude_sessions() + find_codex_sessions()


def find_project_sessions(project_path: Optional[str] = None) -> list[dict]:
    cwd = project_path or os.getcwd()
    sessions = find_all_sessions()

    project_sessions = []
    for s in sessions:
        pp = s.get("project_path", "")
        if pp and (cwd.startswith(pp) or pp.startswith(cwd)):
            project_sessions.append(s)

    if not project_sessions:
        project_sessions = sessions

    def get_mtime(s):
        sp = s.get("source_path", "")
        try:
            return os.path.getmtime(sp)
        except OSError:
            return 0

    project_sessions.sort(key=get_mtime, reverse=True)
    return project_sessions


def find_recent_session(project_path: Optional[str] = None) -> Optional[dict]:
    cwd = project_path or os.getcwd()
    sessions = find_all_sessions()

    project_sessions = []
    for s in sessions:
        pp = s.get("project_path", "")
        if pp and (cwd.startswith(pp) or pp.startswith(cwd)):
            project_sessions.append(s)

    if not project_sessions:
        project_sessions = sessions

    if not project_sessions:
        return None

    def get_mtime(s):
        sp = s.get("source_path", "")
        try:
            return os.path.getmtime(sp)
        except OSError:
            return 0

    project_sessions.sort(key=get_mtime, reverse=True)
    return project_sessions[0]
