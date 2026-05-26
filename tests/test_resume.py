"""Tests for shared resume behavior."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aweshelf.lib.resume import ResumeTarget, build_resume_target, format_resume_target, run_resume_target
from aweshelf.types import Bookmark


def make_bookmark(**kwargs) -> Bookmark:
    defaults = {
        "id": "aweshelf_0001",
        "provider": "claude",
        "session_id": "session-123",
        "title": "Test session",
        "category": "backend",
        "project_path": "",
        "aweswitch_profile": "cc-glm",
    }
    defaults.update(kwargs)
    return Bookmark(**defaults)


class ResumeTests(unittest.TestCase):
    def test_build_resume_target_uses_aweswitch_profile(self):
        bookmark = make_bookmark()

        target = build_resume_target(bookmark, profile_exists=lambda name: name == "cc-glm")

        self.assertEqual(target.argv, ["aweswitch", "cc-glm", "--resume", "session-123"])
        self.assertIsNone(target.cwd)
        self.assertIsNone(target.warning)

    def test_build_resume_target_falls_back_when_profile_missing(self):
        bookmark = make_bookmark()

        target = build_resume_target(bookmark, profile_exists=lambda _name: False)

        self.assertEqual(target.argv, ["claude", "--resume", "session-123"])
        self.assertIn("aweswitch profile 'cc-glm' not found", target.warning)

    def test_build_resume_target_uses_bookmark_project_path_when_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            bookmark = make_bookmark(project_path=tmp, aweswitch_profile=None)

            target = build_resume_target(bookmark)

            self.assertEqual(target.cwd, Path(tmp))

    def test_format_resume_target_quotes_cwd_and_args(self):
        with tempfile.TemporaryDirectory(prefix="project path ") as tmp:
            bookmark = make_bookmark(project_path=tmp, aweswitch_profile=None)
            target = build_resume_target(bookmark)

            formatted = format_resume_target(target)

            self.assertIn("cd ", formatted)
            self.assertIn("claude --resume session-123", formatted)

    def test_run_resume_target_restores_cwd_when_exec_fails(self):
        original_cwd = Path.cwd()
        with tempfile.TemporaryDirectory() as tmp:
            target = ResumeTarget(argv=["definitely-not-aweshelf-command"], cwd=Path(tmp))

            with self.assertRaises(FileNotFoundError):
                run_resume_target(target)

            self.assertEqual(Path.cwd(), original_cwd)


if __name__ == "__main__":
    unittest.main()
