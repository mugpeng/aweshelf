# aweshelf — Session Bookmark Manager

## Problem

Claude Code 和 Codex 产生大量会话，没有内置方式收藏、分类、快速恢复特定会话及其 aweswitch 配置。cc-session 是完整的桌面应用（重），aweshelf 是轻量 CLI-first 工具，附带 TUI 浏览。

## Design Principles

- **80% CLI, 20% TUI**：所有能力都有稳定 CLI 命令，TUI 仅负责浏览和选择
- **最小 bookmark 模型**：只保留找到和恢复会话所需的最少字段
- **aweswitch 原生集成**：bookmark 时自动检测 profile，resume 时自动恢复
- **单 JSON 文件**：无数据库，依赖仅 Click + textual

## Data Model

存储位置：`~/.config/aweshelf/bookmarks.json`

```json
{
  "bookmarks": [
    {
      "id": "bkm_a1b2c3",
      "provider": "claude",
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Fix auth middleware bug",
      "category": "backend",
      "project_path": "/Users/peng/Desktop/Project/my-app",
      "aweswitch_profile": "cc-glm",
      "bookmarked_at": "2026-05-20T14:00:00Z"
    }
  ],
  "version": 1
}
```

字段说明：
- `id` — 自动生成短 ID（`bkm_` + 6 位 hex），作为命令中的 bookmark 标识
- `provider` — `"claude"` 或 `"codex"`
- `session_id` — 原始 session ID
- `title` — 默认从 session 第一条用户消息提取，可用 `-t` 覆盖
- `category` — 自由文本，用户指定（如 `"backend"`, `"research"`）
- `project_path` — session 的工作目录
- `aweswitch_profile` — 自动检测的 aweswitch profile 名（可为 null）
- `bookmarked_at` — ISO 8601 时间戳，自动记录

## Architecture

```
src/aweshelf/
  __init__.py              # Version
  types.py                 # 所有共享类型
  cli.py                   # Click 命令组入口
  commands/
    bookmark.py            # bookmark 命令
    list.py                # list, search, recent 命令
    show.py                # show, edit, rm 命令
    resume.py              # resume 命令
    browse.py              # TUI 入口
  lib/
    store.py               # JSON 文件读写，bookmark CRUD
    discovery.py           # Session 文件发现（Claude JSONL, Codex）
    aweswitch.py           # aweswitch 配置解析，profile 检测
    session.py             # Session 元数据提取
  tui/
    app.py                 # textual App
tests/
  test_store.py
  test_discovery.py
  test_aweswitch.py
  test_session.py
```

分层规则：`cli/` 处理 I/O，`commands/` 处理编排，`lib/` 处理逻辑，`types.py` 处理类型。

## CLI Commands

### bookmark

```bash
# Bookmark 当前项目最近的 session（自动检测）
aweshelf bookmark

# Bookmark 指定 session
aweshelf bookmark <session-id>

# 带选项
aweshelf bookmark <session-id> -t "custom title" -c backend
aweshelf bookmark <session-id> --profile cc-glm

# 交互模式（不带 -t 和 -c 时）
aweshelf bookmark
# → Title: Fix auth middleware bug [auto-detected, Enter to accept]
# → Category: > backend / frontend / infra / [type new]
# → Profile: cc-glm [auto-detected]
```

自动检测流程：
1. 无 session-id → 找当前项目目录下最近修改的 `.jsonl` 文件
2. 从 JSONL 第一条用户消息提取 title
3. 从 session 环境变量匹配 aweswitch profile（比对 `ANTHROPIC_BASE_URL` + `ANTHROPIC_MODEL`）
4. 交互模式下，从已有 bookmarks 动态生成 category 选项

### list & search

```bash
aweshelf list                    # 所有 bookmarks，按 category 分组
aweshelf list -c backend         # 按 category 筛选
aweshelf list -p claude          # 按 provider 筛选
aweshelf search "auth"           # 标题子串匹配
aweshelf recent                  # 最近 10 个
```

输出格式：
```
ID        PROVIDER  TITLE                      CATEGORY   PROFILE
bkm_a1b2  claude    Fix auth middleware bug     backend    cc-glm
bkm_c3d4  codex     Refactor API routes         backend    -
bkm_e5f6  claude    Research vector DB options  research   cc-gemini
```

### show & edit

```bash
aweshelf show <bookmark-id>              # 详情
aweshelf show <bookmark-id> --json       # 原始 JSON

aweshelf edit <bookmark-id> -t "new title"
aweshelf edit <bookmark-id> -c frontend
aweshelf edit <bookmark-id> --profile cc-gemini
```

### resume

```bash
aweshelf resume <bookmark-id>                    # 用保存的 profile 恢复
aweshelf resume <bookmark-id> --profile cc-gemini  # 覆盖 profile
aweshelf resume <bookmark-id> --raw              # 跳过 aweswitch，直接 claude --resume
```

恢复流程：
1. 加载 bookmark
2. 有 `--profile` 用指定的，否则用 `aweswitch_profile`
3. profile 存在于 aweswitch 配置 → `aweswitch <profile> --resume <session-id>`
4. profile 不存在 → 警告，建议 `--raw` 或 `--profile <other>`
5. `--raw` → `claude --resume <session-id>`（或 `codex --resume`）

### rm

```bash
aweshelf rm <bookmark-id>              # 删除
aweshelf rm <bookmark-id> --force      # 跳过确认
```

### browse（TUI）

```bash
aweshelf browse                        # 启动交互浏览器
```

TUI（textual）功能：
- 左栏：bookmark 列表（可按 category/provider 筛选）
- 右栏：选中 bookmark 的详情
- 按键：`Enter` resume，`/` 搜索，`q` 退出
- 无编辑、无创建——仅浏览和选择

## aweswitch 集成

### Profile 检测（bookmark 时）

1. 读 session JSONL 中的环境元数据
2. 加载 `~/.config/aweswitch/config.json`
3. 比对 `ANTHROPIC_BASE_URL` 和 `ANTHROPIC_MODEL`
4. 匹配到 → 存 profile 名；未匹配 → 存 null

### Profile 恢复（resume 时）

1. 读 bookmark 的 `aweswitch_profile`
2. 验证 profile 仍存在于 aweswitch 配置
3. 存在 → `os.execvpe("aweswitch", ["aweswitch", profile, "--resume", session_id], env)`
4. 不存在 → 打印警告，提示 `--raw` 或 `--profile`

## Session 发现

### Claude Code

路径：`~/.claude/projects/{encoded-path}/{session-id}.jsonl`

发现流程：
1. 递归扫描 `~/.claude/projects/` 下的 `.jsonl` 文件
2. 解析前几行提取：session_id, title, model, created_at
3. "当前项目"检测：匹配 `project_path` 与 CWD

### Codex

路径：`~/.codex/sessions/`（JSONL 格式）

发现流程类似。

## 错误处理

- 同一 session_id 重复 bookmark → 警告，跳过（幂等）
- session 文件恢复时不存在 → 错误 + 提示 "Session 文件可能已删除"
- aweswitch profile 缺失 → 警告 + 建议 `--raw` 或 `--profile`
- 无效 bookmark ID → 错误 + 相似 ID 建议

## Dependencies

- `click >= 8.1` — CLI 框架
- `textual >= 0.40` — TUI 框架
- Python >= 3.10

## Testing

- `test_store.py` — JSON CRUD
- `test_discovery.py` — session 文件发现
- `test_aweswitch.py` — profile 匹配
- `test_session.py` — JSONL 解析
- 集成测试：bookmark → list → resume 流程
- TUI：手动测试
