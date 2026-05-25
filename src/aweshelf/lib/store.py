"""JSON file CRUD for bookmarks."""

import json
import os
import secrets
from pathlib import Path
from typing import Optional

from aweshelf.types import Bookmark


CONFIG_DIR = Path("~/.config/aweshelf")


def bookmark_path() -> Path:
    env = os.environ.get("AWESHELF_CONFIG")
    if env:
        return Path(env).expanduser()
    return (CONFIG_DIR / "bookmarks.json").expanduser()


def generate_id() -> str:
    return f"bkm_{secrets.token_hex(3)}"


def load_bookmarks(path: Optional[Path] = None) -> list[Bookmark]:
    path = path or bookmark_path()
    path = Path(path).expanduser()
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return []
    raw = data.get("bookmarks", [])
    return [Bookmark.from_dict(b) for b in raw]


def save_bookmarks(bookmarks: list[Bookmark], path: Optional[Path] = None) -> None:
    path = path or bookmark_path()
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"version": 1, "bookmarks": [b.to_dict() for b in bookmarks]}
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    os.chmod(path, 0o600)


def find_bookmark(bookmark_id: str, path: Optional[Path] = None) -> Optional[Bookmark]:
    bookmarks = load_bookmarks(path)
    for b in bookmarks:
        if b.id == bookmark_id:
            return b
    return None


def find_by_session_id(session_id: str, path: Optional[Path] = None) -> Optional[Bookmark]:
    bookmarks = load_bookmarks(path)
    for b in bookmarks:
        if b.session_id == session_id:
            return b
    return None


def add_bookmark(bookmark: Bookmark, path: Optional[Path] = None) -> Bookmark:
    bookmarks = load_bookmarks(path)
    for b in bookmarks:
        if b.session_id == bookmark.session_id:
            raise ValueError(f"session already bookmarked: {b.id}")
    if not bookmark.id:
        bookmark.id = generate_id()
    bookmarks.append(bookmark)
    save_bookmarks(bookmarks, path)
    return bookmark


def remove_bookmark(bookmark_id: str, path: Optional[Path] = None) -> bool:
    bookmarks = load_bookmarks(path)
    new_bookmarks = [b for b in bookmarks if b.id != bookmark_id]
    if len(new_bookmarks) == len(bookmarks):
        return False
    save_bookmarks(new_bookmarks, path)
    return True


def update_bookmark(bookmark_id: str, path: Optional[Path] = None, **fields) -> Optional[Bookmark]:
    bookmarks = load_bookmarks(path)
    for b in bookmarks:
        if b.id == bookmark_id:
            for key, value in fields.items():
                if hasattr(b, key) and value is not None:
                    setattr(b, key, value)
            save_bookmarks(bookmarks, path)
            return b
    return None


def list_categories(path: Optional[Path] = None) -> list[str]:
    bookmarks = load_bookmarks(path)
    cats = sorted(set(b.category for b in bookmarks if b.category))
    return cats
