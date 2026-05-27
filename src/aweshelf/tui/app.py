"""TUI browse app using textual."""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Footer, Header, Input, Static

from aweshelf.lib.store import load_bookmarks
from aweshelf.types import Bookmark

SIDEBAR_FRAC = 60
DETAIL_FRAC = 40
MIN_FRAC = 10


class DragHandle(Static):
    """1-cell vertical divider that can be dragged to resize panels."""

    can_focus = False

    DEFAULT_CSS = """
    DragHandle {
        width: 1;
        height: 1fr;
        background: $primary-background;
    }
    """

    def on_mouse_down(self, event) -> None:
        app = self.app
        app._dragging = True
        app._drag_start_x = event.screen_x
        sidebar = app.query_one("#sidebar")
        detail = app.query_one("#detail")
        app._drag_start_sidebar = int(sidebar.styles.width.value) if sidebar.styles.width else SIDEBAR_FRAC
        app._drag_start_detail = int(detail.styles.width.value) if detail.styles.width else DETAIL_FRAC
        self.capture_mouse()

    def on_mouse_move(self, event) -> None:
        app = self.app
        if not app._dragging:
            return
        total = app._drag_start_sidebar + app._drag_start_detail
        delta = event.screen_x - app._drag_start_x
        new_sidebar = max(MIN_FRAC, min(total - MIN_FRAC, app._drag_start_sidebar + delta))
        app.query_one("#sidebar").styles.width = f"{new_sidebar}fr"
        app.query_one("#detail").styles.width = f"{total - new_sidebar}fr"

    def on_mouse_up(self, event) -> None:
        if self.app._dragging:
            self.app._dragging = False
            self.release_mouse()


class BookmarkBrowser(App):
    """Browse and select bookmarks."""

    EMPTY_MESSAGE = "No bookmarks found. Run aweshelf bookmark first."
    HELP_TEXT = "\n".join([
        "/      Filter bookmarks",
        "Esc    Clear filter / return to table",
        "Enter  Resume selected bookmark",
        "r      Resume selected bookmark",
        "?      Show this help",
        "q      Quit",
        "[ / ]  Shrink / grow sidebar",
    ])

    BINDINGS = [
        Binding("enter", "resume", "Resume", show=False),
        Binding("q", "quit", "Quit"),
        Binding("r", "resume", "Resume"),
        Binding("?", "help", "Help"),
        Binding("slash", "focus_search", "Filter", show=False),
        Binding("escape", "clear_search", "Clear", show=False),
        Binding("[", "resize_sidebar(-5)", "Shrink sidebar", show=False),
        Binding("]", "resize_sidebar(5)", "Grow sidebar", show=False),
    ]

    CSS = """
    Screen {
        layout: horizontal;
    }
    #sidebar {
        width: 60fr;
    }
    #search {
        display: none;
        dock: top;
        height: 3;
        margin: 0 1;
    }
    #search.visible {
        display: block;
    }
    #detail {
        width: 40fr;
        padding: 1 2;
    }
    #detail-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    """

    def __init__(self):
        super().__init__()
        self._bookmarks: list[Bookmark] = []
        self._selected: Bookmark | None = None
        self._filter: str = ""
        self._dragging: bool = False
        self._drag_start_x: int = 0
        self._drag_start_sidebar: int = SIDEBAR_FRAC
        self._drag_start_detail: int = DETAIL_FRAC

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Input(placeholder="Filter bookmarks...", id="search")
                yield DataTable(id="table")
            yield DragHandle()
            with Vertical(id="detail"):
                yield Static("Select a bookmark to view details.", id="detail-title")
                yield Static("", id="detail-body")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#table", DataTable)
        table.add_columns("ID", "PROVIDER", "TITLE", "CATEGORY", "PROFILE")
        table.cursor_type = "row"
        self._load_data()

    def _matches_filter(self, b: Bookmark) -> bool:
        if not self._filter:
            return True
        f = self._filter
        return (
            f in b.title.lower()
            or f in b.category.lower()
            or f in b.session_id.lower()
            or f in b.project_path.lower()
            or (b.aweswitch_profile and f in b.aweswitch_profile.lower())
        )

    def _load_data(self) -> None:
        table = self.query_one("#table", DataTable)
        table.clear()
        self._bookmarks = load_bookmarks()
        visible = [b for b in self._bookmarks if self._matches_filter(b)]
        if not visible:
            msg = self.EMPTY_MESSAGE if not self._bookmarks else "No matches."
            self.query_one("#detail-title", Static).update(msg)
            self.query_one("#detail-body", Static).update(self.HELP_TEXT)
            return
        for b in visible:
            table.add_row(
                b.id,
                b.provider,
                b.title[:50] + ("..." if len(b.title) > 50 else ""),
                b.category or "-",
                b.aweswitch_profile or "-",
                key=b.id,
            )

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search":
            self._filter = event.value.lower()
            self._load_data()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if self._dragging:
            return
        bookmark_id = event.row_key.value
        for b in self._bookmarks:
            if b.id == bookmark_id:
                self._selected = b
                self._update_detail(b)
                self.exit(result=b)
                return

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if self._dragging or event.row_key is None:
            return
        bookmark_id = event.row_key.value
        for b in self._bookmarks:
            if b.id == bookmark_id:
                self._selected = b
                self._update_detail(b)
                break

    def _update_detail(self, b: Bookmark) -> None:
        self.query_one("#detail-title", Static).update(f" {b.title}")
        lines = [
            f"ID:        {b.id}",
            f"Provider:  {b.provider}",
            f"Session:   {b.session_id}",
            f"Category:  {b.category or '-'}",
            f"Project:   {b.project_path or '-'}",
            f"Profile:   {b.aweswitch_profile or '-'}",
            f"Saved at:  {b.bookmarked_at}",
        ]
        self.query_one("#detail-body", Static).update("\n".join(lines))

    def action_resume(self) -> None:
        if self._selected:
            self.exit(result=self._selected)

    def action_resize_sidebar(self, delta: int) -> None:
        total = SIDEBAR_FRAC + DETAIL_FRAC
        sidebar = self.query_one("#sidebar")
        current = int(sidebar.styles.width.value) if sidebar.styles.width else SIDEBAR_FRAC
        new = max(MIN_FRAC, min(total - MIN_FRAC, current + delta))
        sidebar.styles.width = f"{new}fr"
        self.query_one("#detail").styles.width = f"{total - new}fr"

    def action_help(self) -> None:
        self.query_one("#detail-title", Static).update("Keyboard shortcuts")
        self.query_one("#detail-body", Static).update(self.HELP_TEXT)

    def action_focus_search(self) -> None:
        search = self.query_one("#search", Input)
        search.add_class("visible")
        search.focus()

    def action_clear_search(self) -> None:
        search = self.query_one("#search", Input)
        if search.has_class("visible"):
            search.remove_class("visible")
            self._filter = ""
            search.value = ""
            self._load_data()
            self.query_one("#table", DataTable).focus()
