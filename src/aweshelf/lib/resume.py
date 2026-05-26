"""Shared resume target construction and execution."""

import os
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from aweshelf.lib.aweswitch import build_resume_command, profile_exists as default_profile_exists
from aweshelf.types import Bookmark


@dataclass
class ResumeTarget:
    argv: list[str]
    cwd: Optional[Path] = None
    warning: Optional[str] = None


class ResumeError(ValueError):
    pass


def build_resume_target(
    bookmark: Bookmark,
    profile_override: Optional[str] = None,
    raw: bool = False,
    profile_exists: Callable[[str], bool] = default_profile_exists,
) -> ResumeTarget:
    use_profile = profile_override or bookmark.aweswitch_profile
    warning = None
    if use_profile and not raw and not profile_exists(use_profile):
        if profile_override:
            raise ResumeError(
                f"aweswitch profile '{use_profile}' not found. Use --raw to skip aweswitch."
            )
        warning = f"aweswitch profile '{use_profile}' not found; falling back to raw resume."
        use_profile = None
        raw = True

    cwd = _valid_project_path(bookmark.project_path)
    argv = build_resume_command(bookmark.provider, use_profile, bookmark.session_id, raw=raw)
    return ResumeTarget(argv=argv, cwd=cwd, warning=warning)


def format_resume_target(target: ResumeTarget) -> str:
    command = " ".join(shlex.quote(part) for part in target.argv)
    if target.cwd is None:
        return command
    return f"cd {shlex.quote(str(target.cwd))} && {command}"


def run_resume_target(target: ResumeTarget) -> None:
    original_cwd = os.getcwd()
    try:
        if target.cwd is not None:
            os.chdir(target.cwd)
        os.execvpe(target.argv[0], target.argv, os.environ)
    except Exception:
        os.chdir(original_cwd)
        raise


def _valid_project_path(project_path: str) -> Optional[Path]:
    if not project_path:
        return None
    path = Path(project_path).expanduser()
    if path.exists() and path.is_dir():
        return path
    return None
