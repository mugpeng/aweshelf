"""Shared types for aweshelf."""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Bookmark:
    id: str
    provider: str  # "claude" or "codex"
    session_id: str
    title: str
    category: str
    project_path: str
    aweswitch_profile: Optional[str] = None
    bookmarked_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Bookmark":
        return cls(
            id=data["id"],
            provider=data["provider"],
            session_id=data["session_id"],
            title=data["title"],
            category=data.get("category", ""),
            project_path=data.get("project_path", ""),
            aweswitch_profile=data.get("aweswitch_profile"),
            bookmarked_at=data.get("bookmarked_at", datetime.now(timezone.utc).isoformat()),
        )
