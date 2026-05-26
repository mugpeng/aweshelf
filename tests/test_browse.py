"""Tests for browse TUI configuration."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

try:
    from aweshelf.tui.app import BookmarkBrowser
except ImportError:
    BookmarkBrowser = None


@unittest.skipIf(BookmarkBrowser is None, "textual is not installed")
class BrowseTests(unittest.TestCase):
    def test_help_binding_is_available(self):
        keys = {binding.key for binding in BookmarkBrowser.BINDINGS}
        self.assertIn("?", keys)

    def test_empty_message_is_actionable(self):
        self.assertIn("aweshelf bookmark", BookmarkBrowser.EMPTY_MESSAGE)

    def test_help_text_lists_resume_and_quit(self):
        self.assertIn("Enter", BookmarkBrowser.HELP_TEXT)
        self.assertIn("q", BookmarkBrowser.HELP_TEXT)


if __name__ == "__main__":
    unittest.main()
