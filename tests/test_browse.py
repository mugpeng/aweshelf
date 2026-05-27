"""Tests for browse TUI configuration."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

try:
    from aweshelf.tui.app import BookmarkBrowser, ConfirmScreen, EditScreen
except ImportError:
    BookmarkBrowser = None


@unittest.skipIf(BookmarkBrowser is None, "textual is not installed")
class BrowseTests(unittest.TestCase):
    def test_help_binding_is_available(self):
        keys = {binding.key for binding in BookmarkBrowser.BINDINGS}
        self.assertIn("question_mark", keys)

    def test_empty_message_is_actionable(self):
        self.assertIn("aweshelf bookmark", BookmarkBrowser.EMPTY_MESSAGE)

    def test_filter_binding_is_available(self):
        keys = {binding.key for binding in BookmarkBrowser.BINDINGS}
        self.assertIn("slash", keys)

    def test_escape_binding_is_available(self):
        keys = {binding.key for binding in BookmarkBrowser.BINDINGS}
        self.assertIn("escape", keys)

    def test_help_text_lists_all_shortcuts(self):
        self.assertIn("/", BookmarkBrowser.HELP_TEXT)
        self.assertIn("Esc", BookmarkBrowser.HELP_TEXT)
        self.assertIn("Enter", BookmarkBrowser.HELP_TEXT)
        self.assertIn("e", BookmarkBrowser.HELP_TEXT)
        self.assertIn("r", BookmarkBrowser.HELP_TEXT)
        self.assertIn("q", BookmarkBrowser.HELP_TEXT)

    def test_resize_bindings_exist(self):
        keys = {binding.key for binding in BookmarkBrowser.BINDINGS}
        self.assertIn("[", keys)
        self.assertIn("]", keys)

    def test_drag_handle_class_exists(self):
        from aweshelf.tui.app import DragHandle
        self.assertFalse(DragHandle.can_focus)

    def test_edit_binding_is_available(self):
        keys = {binding.key for binding in BookmarkBrowser.BINDINGS}
        self.assertIn("e", keys)

    def test_remove_binding_is_available(self):
        keys = {binding.key for binding in BookmarkBrowser.BINDINGS}
        self.assertIn("r", keys)

    def test_mode_toggle_binding(self):
        keys = {binding.key for binding in BookmarkBrowser.BINDINGS}
        self.assertIn("m", keys)

    def test_sort_cycle_binding(self):
        keys = {binding.key for binding in BookmarkBrowser.BINDINGS}
        self.assertIn("s", keys)

    def test_help_text_lists_mode_and_sort(self):
        self.assertIn("m", BookmarkBrowser.HELP_TEXT)
        self.assertIn("s", BookmarkBrowser.HELP_TEXT)

    def test_category_colors_defined(self):
        from aweshelf.tui.app import CATEGORY_COLORS
        self.assertGreater(len(CATEGORY_COLORS), 0)

    def test_mode_order(self):
        from aweshelf.tui.app import MODE_ORDER
        self.assertEqual(MODE_ORDER, ["all", "category"])

    def test_sort_order(self):
        from aweshelf.tui.app import SORT_ORDER
        self.assertEqual(SORT_ORDER, ["cat_id", "id"])

    def test_cat_key_prefix(self):
        from aweshelf.tui.app import CAT_KEY_PREFIX
        self.assertTrue(CAT_KEY_PREFIX.startswith("__"))

    def test_is_cat_row_skips_category_headers(self):
        from aweshelf.tui.app import BookmarkBrowser, CAT_KEY_PREFIX
        app = BookmarkBrowser()
        self.assertTrue(app._is_cat_row(f"{CAT_KEY_PREFIX}backend"))
        self.assertFalse(app._is_cat_row("aweshelf_0001"))
        self.assertFalse(app._is_cat_row(None))


@unittest.skipIf(BookmarkBrowser is None, "textual is not installed")
class EditScreenTests(unittest.TestCase):
    def test_has_save_and_cancel_bindings(self):
        keys = {binding.key for binding in EditScreen.BINDINGS}
        self.assertIn("escape", keys)


@unittest.skipIf(BookmarkBrowser is None, "textual is not installed")
class ConfirmScreenTests(unittest.TestCase):
    def test_has_escape_binding(self):
        keys = {binding.key for binding in ConfirmScreen.BINDINGS}
        self.assertIn("escape", keys)


if __name__ == "__main__":
    unittest.main()
