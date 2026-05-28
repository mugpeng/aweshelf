# Aweshelf for VS Code

Browse, search, edit, and resume aweshelf AI coding session bookmarks from VS Code.

## Requirements

- Python `aweshelf` CLI installed and available on `PATH`, or configure `aweshelf.commandPath`.
- Optional: `aweswitch` for Claude profile-based resume.

During development inside the aweshelf repository, the extension automatically uses `../../.venv/bin/aweshelf` when it exists.

## Features

- Bookmark sidebar grouped by category.
- Search, sort by title/recent/ID, filter by provider/category, and auto-refresh on bookmark-store changes.
- Bookmark current session or choose a discovered session through QuickPick.
- Show bookmark details as Markdown.
- Edit title, category, and aweswitch profile.
- Remove bookmarks with confirmation.
- Resume normally, resume raw, or resume with a selected profile.
- Copy session ID or exact resume command.
- Open the bookmarked project path.
- Show current aweshelf command/config/status.

## Settings

```json
{
  "aweshelf.commandPath": "aweshelf",
  "aweshelf.configPath": ""
}
```

`aweshelf.configPath` maps to `AWESHELF_CONFIG`. Leave it empty to use `~/.config/aweshelf/bookmarks.json`.

## Development

```bash
cd extensions/vscode
npm install
npm run compile
```

Open this folder in VS Code and run `Run Aweshelf Extension` from the Run and Debug view.

## Package

```bash
cd extensions/vscode
npm run package
```
