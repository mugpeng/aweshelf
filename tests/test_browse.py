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
        self.assertIn("y", BookmarkBrowser.HELP_TEXT)
        self.assertIn("n", BookmarkBrowser.HELP_TEXT)

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
        self.assertIn("c", keys)
        self.assertNotIn("m", keys)

    def test_sort_cycle_binding(self):
        keys = {binding.key for binding in BookmarkBrowser.BINDINGS}
        self.assertIn("s", keys)

    def test_help_text_lists_mode_and_sort(self):
        self.assertIn("c", BookmarkBrowser.HELP_TEXT)
        self.assertNotIn("m      Toggle Category", BookmarkBrowser.HELP_TEXT)
        self.assertIn("s", BookmarkBrowser.HELP_TEXT)
        self.assertIn("Category", BookmarkBrowser.HELP_TEXT)
        self.assertNotIn("mode", BookmarkBrowser.HELP_TEXT.lower())

    def test_category_colors_defined(self):
        from aweshelf.tui.app import CATEGORY_COLORS
        self.assertGreater(len(CATEGORY_COLORS), 0)

    def test_mode_order(self):
        from aweshelf.tui.app import MODE_ORDER
        self.assertEqual(MODE_ORDER, ["category", "all"])

    def test_default_mode_is_category(self):
        app = BookmarkBrowser()
        self.assertEqual(app._mode, "category")

    def test_browse_columns_align_with_list(self):
        from aweshelf.tui.app import ALL_COLUMNS, CATEGORY_COLUMNS
        self.assertEqual(ALL_COLUMNS, ["ID", "PROVIDER", "TITLE", "CATEGORY", "PROFILE", "SESSION"])
        self.assertEqual(CATEGORY_COLUMNS, ["ID", "PROVIDER", "TITLE", "PROFILE", "SESSION"])

    def test_sort_order(self):
        from aweshelf.tui.app import SORT_ORDER
        self.assertEqual(SORT_ORDER, ["cat_id", "id"])

    def test_cat_key_prefix(self):
        from aweshelf.tui.app import CAT_KEY_PREFIX
        self.assertTrue(CAT_KEY_PREFIX.startswith("__"))

    def test_is_cat_row_skips_category_headers(self):
        from aweshelf.tui.app import CAT_KEY_PREFIX
        app = BookmarkBrowser()
        self.assertTrue(app._is_cat_row(f"{CAT_KEY_PREFIX}backend"))
        self.assertFalse(app._is_cat_row("aweshelf_0001"))
        self.assertFalse(app._is_cat_row(None))

    def test_enter_binding_has_priority(self):
        enter_bindings = [b for b in BookmarkBrowser.BINDINGS if b.key == "enter"]
        self.assertTrue(enter_bindings[0].priority)

    def test_mode_constants_exist(self):
        from aweshelf.tui.app import MODE_NORMAL, MODE_EDIT, MODE_CONFIRM_RESUME, MODE_CONFIRM_REMOVE
        self.assertEqual(MODE_NORMAL, "normal")
        self.assertEqual(MODE_EDIT, "edit")
        self.assertEqual(MODE_CONFIRM_RESUME, "confirm_resume")
        self.assertEqual(MODE_CONFIRM_REMOVE, "confirm_remove")


if __name__ == "__main__":
    unittest.main()
