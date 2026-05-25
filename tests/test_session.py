"""Tests for lib/session.py."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aweshelf.lib.session import parse_session_meta, detect_provider, extract_title_from_messages, clean_title


def write_jsonl(path: Path, entries: list[dict]) -> None:
    with open(path, "w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")


class SessionTests(unittest.TestCase):
    def test_detect_provider_claude(self):
        self.assertEqual(detect_provider(Path("/home/user/.claude/projects/test.jsonl")), "claude")

    def test_detect_provider_codex(self):
        self.assertEqual(detect_provider(Path("/home/user/.codex/sessions/test.jsonl")), "codex")

    def test_clean_title_strips_tags(self):
        self.assertEqual(clean_title("<command-message>test</command-message>"), "test")
        self.assertEqual(clean_title("<local-command-caveat>hello</local-command-caveat> world"), "hello world")

    def test_detect_provider_unknown(self):
        self.assertEqual(detect_provider(Path("/tmp/test.jsonl")), "claude")

    def test_extract_title_from_user_message(self):
        messages = [{"role": "user", "content": "Fix the auth bug"}]
        title = extract_title_from_messages(messages)
        self.assertEqual(title, "Fix the auth bug")

    def test_extract_title_truncates_long(self):
        long_text = "x" * 100
        messages = [{"role": "user", "content": long_text}]
        title = extract_title_from_messages(messages)
        self.assertTrue(len(title) <= 80)
        self.assertTrue(title.endswith("..."))

    def test_extract_title_from_content_list(self):
        messages = [{"role": "user", "content": [{"type": "text", "text": "Hello"}]}]
        title = extract_title_from_messages(messages)
        self.assertEqual(title, "Hello")

    def test_extract_title_from_first_message(self):
        messages = [
            {"content": "Fix bug"},
        ]
        title = extract_title_from_messages(messages)
        self.assertEqual(title, "Fix bug")

    def test_parse_session_meta_from_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test-session.jsonl"
            write_jsonl(path, [
                {"type": "summary", "sessionId": "abc-123", "cwd": "/home/user/project"},
                {"role": "user", "content": "Help me fix this bug"},
                {"role": "assistant", "content": "Sure", "model": "claude-sonnet-4-20250514"},
            ])
            meta = parse_session_meta(path)
            self.assertEqual(meta["session_id"], "abc-123")
            self.assertEqual(meta["title"], "Help me fix this bug")
            self.assertEqual(meta["model"], "claude-sonnet-4-20250514")
            self.assertEqual(meta["project_path"], "/home/user/project")
            self.assertEqual(meta["provider"], "claude")

    def test_parse_session_meta_fallback_session_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "my-session-id.jsonl"
            write_jsonl(path, [{"role": "user", "content": "Hello"}])
            meta = parse_session_meta(path)
            self.assertEqual(meta["session_id"], "my-session-id")

    def test_parse_session_meta_empty_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "empty.jsonl"
            path.write_text("")
            meta = parse_session_meta(path)
            self.assertEqual(meta["title"], "Untitled session")


if __name__ == "__main__":
    unittest.main()
