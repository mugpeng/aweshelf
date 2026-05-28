import assert from "node:assert/strict";
import test from "node:test";

import {
  buildBookmarkCurrentArgs,
  buildBookmarkSessionArgs,
  buildEditArgs,
  buildListArgs,
  buildProfilesArgs,
  buildRemoveArgs,
  buildResumeArgs,
  buildResumeDryRunArgs,
  buildSessionsArgs,
  buildShowArgs,
  buildShellCommand,
  buildVersionArgs,
  createAweshelfEnv,
  formatCommandError,
  isCommandNotFoundError,
  resolveBookmarkConfigPath,
  resolveCommandPath
} from "../src/aweshelfService";

test("buildListArgs uses list JSON output when no query is provided", () => {
  assert.deepEqual(buildListArgs("  "), ["list", "--json"]);
});

test("buildListArgs uses search JSON output when a query is provided", () => {
  assert.deepEqual(buildListArgs("auth bug"), ["search", "auth bug", "--json"]);
});

test("buildVersionArgs checks aweshelf availability without reading user data", () => {
  assert.deepEqual(buildVersionArgs(), ["--version"]);
});

test("buildResumeArgs targets the selected bookmark", () => {
  assert.deepEqual(buildResumeArgs("aweshelf_0001"), ["resume", "aweshelf_0001"]);
});

test("buildBookmarkCurrentArgs bookmarks the current project session", () => {
  assert.deepEqual(buildBookmarkCurrentArgs(), ["bookmark", "--current"]);
});

test("buildBookmarkSessionArgs adds non-interactive metadata fields", () => {
  assert.deepEqual(
    buildBookmarkSessionArgs("sess-001", {
      title: "Fix auth",
      category: "backend",
      profile: "cc-glm"
    }),
    ["bookmark", "sess-001", "--title", "Fix auth", "--category", "backend", "--profile", "cc-glm"]
  );
});

test("buildShowArgs requests JSON details for one bookmark", () => {
  assert.deepEqual(buildShowArgs("aweshelf_0001"), ["show", "aweshelf_0001", "--json"]);
});

test("buildEditArgs includes only fields that were provided", () => {
  assert.deepEqual(
    buildEditArgs("aweshelf_0001", {
      title: "New title",
      category: "",
      profile: undefined
    }),
    ["edit", "aweshelf_0001", "--title", "New title", "--category", ""]
  );
});

test("buildEditArgs rejects calls without editable fields", () => {
  assert.throws(
    () => buildEditArgs("aweshelf_0001", {}),
    /at least one field/
  );
});

test("buildRemoveArgs removes without prompting", () => {
  assert.deepEqual(buildRemoveArgs("aweshelf_0001"), ["rm", "aweshelf_0001", "--force"]);
});

test("buildSessionsArgs requests JSON sessions with optional limit", () => {
  assert.deepEqual(buildSessionsArgs(10), ["sessions", "--json", "--limit", "10"]);
  assert.deepEqual(buildSessionsArgs(0), ["sessions", "--json", "--limit", "0"]);
});

test("buildProfilesArgs requests JSON profiles with optional provider", () => {
  assert.deepEqual(buildProfilesArgs(), ["profiles", "--json"]);
  assert.deepEqual(buildProfilesArgs("claude"), ["profiles", "--json", "--provider", "claude"]);
});

test("buildResumeDryRunArgs includes profile override and raw mode", () => {
  assert.deepEqual(
    buildResumeDryRunArgs("aweshelf_0001", { profile: "cc-glm" }),
    ["resume", "aweshelf_0001", "--dry-run", "--json", "--profile", "cc-glm"]
  );
  assert.deepEqual(
    buildResumeDryRunArgs("aweshelf_0001", { raw: true }),
    ["resume", "aweshelf_0001", "--dry-run", "--json", "--raw"]
  );
});

test("buildShellCommand quotes arguments for terminal execution", () => {
  assert.equal(
    buildShellCommand("aweshelf", ["resume", "aweshelf 0001"]),
    "aweshelf resume 'aweshelf 0001'"
  );
});

test("createAweshelfEnv adds AWESHELF_CONFIG only when configured", () => {
  assert.deepEqual(createAweshelfEnv(""), undefined);
  assert.deepEqual(createAweshelfEnv("/tmp/bookmarks.json"), {
    AWESHELF_CONFIG: "/tmp/bookmarks.json"
  });
});

test("resolveCommandPath keeps an explicitly configured command", () => {
  assert.equal(
    resolveCommandPath("/opt/bin/aweshelf", "/repo/extensions/vscode", () => true),
    "/opt/bin/aweshelf"
  );
});

test("resolveCommandPath falls back to repo venv during extension development", () => {
  assert.equal(
    resolveCommandPath("aweshelf", "/repo/extensions/vscode", (candidate: string) =>
      candidate === "/repo/.venv/bin/aweshelf"
    ),
    "/repo/.venv/bin/aweshelf"
  );
});

test("resolveBookmarkConfigPath uses configured path or XDG default", () => {
  assert.equal(
    resolveBookmarkConfigPath("/tmp/bookmarks.json", "/home/user"),
    "/tmp/bookmarks.json"
  );
  assert.equal(
    resolveBookmarkConfigPath("", "/home/user"),
    "/home/user/.config/aweshelf/bookmarks.json"
  );
});

test("formatCommandError explains missing aweshelf executable", () => {
  assert.match(
    formatCommandError({ code: "ENOENT", path: "aweshelf" }),
    /aweshelf executable was not found/
  );
});

test("isCommandNotFoundError only matches ENOENT", () => {
  assert.equal(isCommandNotFoundError({ code: "ENOENT" }), true);
  assert.equal(isCommandNotFoundError({ code: "EACCES" }), false);
  assert.equal(isCommandNotFoundError(new Error("boom")), false);
});

test("formatCommandError includes stderr from failed commands", () => {
  assert.equal(
    formatCommandError({ stderr: "Error: bookmark not found: aweshelf_9999\n" }),
    "Error: bookmark not found: aweshelf_9999"
  );
});
