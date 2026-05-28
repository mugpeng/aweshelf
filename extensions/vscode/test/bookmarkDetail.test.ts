import assert from "node:assert/strict";
import test from "node:test";

import { formatBookmarkDetailMarkdown } from "../src/bookmarkDetail";

test("formatBookmarkDetailMarkdown renders bookmark metadata and first prompt", () => {
  const markdown = formatBookmarkDetailMarkdown({
    id: "aweshelf_0001",
    provider: "claude",
    session_id: "sess-001",
    title: "Fix auth",
    category: "backend",
    project_path: "/tmp/project",
    first_prompt: "Investigate auth middleware",
    aweswitch_profile: "cc-glm",
    bookmarked_at: "2026-05-20T10:00:00+00:00"
  });

  assert.match(markdown, /^# Fix auth/);
  assert.match(markdown, /- \*\*ID:\*\* `aweshelf_0001`/);
  assert.match(markdown, /- \*\*aweswitch profile:\*\* `cc-glm`/);
  assert.match(markdown, /Investigate auth middleware/);
});
