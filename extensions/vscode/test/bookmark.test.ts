import assert from "node:assert/strict";
import test from "node:test";

import { filterBookmarks, groupBookmarks } from "../src/bookmark";

test("groupBookmarks groups by category and keeps uncategorized last", () => {
  const groups = groupBookmarks([
    {
      id: "aweshelf_0002",
      provider: "codex",
      session_id: "sess-002",
      title: "Write UI",
      category: "",
      project_path: "/tmp/project",
      bookmarked_at: "2026-05-21T10:00:00+00:00"
    },
    {
      id: "aweshelf_0001",
      provider: "claude",
      session_id: "sess-001",
      title: "Fix auth",
      category: "backend",
      project_path: "/tmp/project",
      aweswitch_profile: "cc-glm",
      bookmarked_at: "2026-05-20T10:00:00+00:00"
    }
  ]);

  assert.deepEqual(groups.map((group) => group.category), ["backend", "Uncategorized"]);
  assert.equal(groups[0].bookmarks[0].id, "aweshelf_0001");
  assert.equal(groups[1].bookmarks[0].id, "aweshelf_0002");
});

test("groupBookmarks can sort bookmarks by recent timestamp", () => {
  const groups = groupBookmarks([
    {
      id: "aweshelf_0001",
      provider: "claude",
      session_id: "sess-001",
      title: "Older",
      category: "backend",
      project_path: "/tmp/project",
      bookmarked_at: "2026-05-20T10:00:00+00:00"
    },
    {
      id: "aweshelf_0002",
      provider: "claude",
      session_id: "sess-002",
      title: "Newer",
      category: "backend",
      project_path: "/tmp/project",
      bookmarked_at: "2026-05-21T10:00:00+00:00"
    }
  ], { sortBy: "recent" });

  assert.deepEqual(groups[0].bookmarks.map((bookmark) => bookmark.id), [
    "aweshelf_0002",
    "aweshelf_0001"
  ]);
});

test("filterBookmarks filters by provider and category", () => {
  const bookmarks = [
    {
      id: "aweshelf_0001",
      provider: "claude",
      session_id: "sess-001",
      title: "Fix auth",
      category: "backend",
      project_path: "/tmp/project",
      bookmarked_at: "2026-05-20T10:00:00+00:00"
    },
    {
      id: "aweshelf_0002",
      provider: "codex",
      session_id: "sess-002",
      title: "Write UI",
      category: "frontend",
      project_path: "/tmp/project",
      bookmarked_at: "2026-05-21T10:00:00+00:00"
    }
  ];

  assert.deepEqual(
    filterBookmarks(bookmarks, { provider: "codex" }).map((bookmark) => bookmark.id),
    ["aweshelf_0002"]
  );
  assert.deepEqual(
    filterBookmarks(bookmarks, { category: "backend" }).map((bookmark) => bookmark.id),
    ["aweshelf_0001"]
  );
});
