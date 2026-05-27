"""Backwards-compatible shim. Import from aweshelf.lib.resume_target instead."""

from aweshelf.lib.resume_target import (  # noqa: F401
    ResumeTarget,
    ResumeError,
    build_resume_target,
    format_resume_target,
    run_resume_target,
    execute_resume,
)
