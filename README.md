# Ticket Pilot 🎫✈️

**多 Agent 通用的 Linear ↔ GitHub issue 同步 Skill。**

Ticket Pilot 让任何 AI Agent（Hermes、Claude Code、Codex、OpenClaw、Cursor、Gemini CLI）都能在处理 Linear issue 时自动与 GitHub 保持同步。当你开始处理一个 Linear issue 时，Agent 会自动：

- 在 GitHub 创建对应的镜像 issue（1:1 映射）
- 在**两个平台**同步发布进度评论（按阶段更新，不是每步都发）
- 在 Linear 上追踪状态（Linear 是唯一真相源）
- 涉及写代码时，可选创建 branch / commit / PR

## 快速安装

### 一次装到所有 Agent（通用安装器）
```bash
npx agent-skills-cli install
```

### 手动安装 — 选择你的 Agent

| Agent | 安装命令 |
|-------|---------|
| **Claude Code** | `cp -r ticket-pilot/ ~/.claude/skills/ticket-pilot/` |
| **Codex** | `cp -r ticket-pilot/ ~/.codex/skills/ticket-pilot/` |
| **Hermes** | `cp -r ticket-pilot/ ~/.hermes/skills/productivity/ticket-pilot/` |
| **OpenClaw** | `cp -r ticket-pilot/ ~/.openclaw/skills/ticket-pilot/` |
| **Cursor** | `cp -r ticket-pilot/ .cursor/skills/ticket-pilot/` |
| **Gemini CLI** | `cp -r ticket-pilot/ .gemini/skills/ticket-pilot/` |

### 从源码安装
```bash
git clone https://github.com/RachelXiaolan/ticket-pilot.git
cd ticket-pilot
# 然后复制到你使用的 Agent 的 skills 目录（见上表）
```

## 前置条件

### Linear
- 在 https://linear.app/settings/account/security → Personal API keys 创建个人 API key
- 设置为环境变量 `LINEAR_API_KEY`

### GitHub（三选一）
- **gh CLI**（推荐）：运行 `gh auth login`
- **Personal Access Token**：设置为环境变量 `GITHUB_TOKEN`
- **GitHub MCP / App**：如果已经配置过，可直接使用

## 首次使用

首次使用 Ticket Pilot 时，Agent 会：
1. 验证 Linear + GitHub 认证
2. 自动发现你的工作区信息：team、project、label、用户
3. 让你选择默认值（team、project、label、assignee）
4. 保存到 `~/.ticket-pilot/settings.md`

之后创建 issue 时自动使用默认值。创建时直接说明即可覆盖默认值（如"在 SBY team 建个 issue"、"assign 给 Leo"）。

## 工作原理

```
Linear Issue（唯一真相源）
  ├── 状态 / 优先级 / assignee / label
  ├── 进度评论 ──→ 镜像到 GitHub issue
  │
  └── ←── 链接 ──→ GitHub Issue（镜像）
                       ├── 同步的评论
                       ├──（可选）branch + commit + PR
                       └──（可选）labels / assignees
```

### 评论风格
- **按阶段更新，不按 prompt 更新** — 多个相关步骤属于同一阶段时，等阶段结束再发一条评论
- **每条评论必须包含**：谁做的（Agent 名称）、做了什么、关键产出（链接）
- 简洁、可扫读，不要大段文字

### Issue 创建
- 自动检测并遵循你 team 的命名规范
- 自动应用你的默认 label + assignee
- 同时在 GitHub 创建对应 issue，互相链接

## 支持的 Agent

Ticket Pilot 使用 [Agent Skills 开放标准](https://github.com/anthropics/skills)（`SKILL.md` + YAML frontmatter）。任何支持此标准的 Agent 都可以使用。

| Agent | Skills 目录 | 激活方式 |
|-------|-----------|---------|
| Claude Code | `~/.claude/skills/` | 原生支持 |
| OpenAI Codex | `~/.codex/skills/` | 自动发现 |
| Hermes Agent | `~/.hermes/skills/` | 原生支持 |
| OpenClaw | `~/.openclaw/skills/` | YAML frontmatter 触发 |
| Cursor | `.cursor/skills/` | `@ticket-pilot` |
| Gemini CLI | `.gemini/skills/` | `activate_skill()` |

## 文件结构

```
ticket-pilot/
├── SKILL.md                          # 主技能文件
├── README.md                         # 本文件（中文版）
├── README_EN.md                      # 英文版
├── references/
│   ├── onboarding-settings.md        # 首次配置格式
│   ├── state-model.md                # Linear 状态映射
│   ├── github-conventions.md         # branch/commit/PR 约定
│   └── workflow-template.md          # 验证过的工作流示例
└── scripts/
    ├── init_task_record.py           # task artifact 骨架
    └── sync_comment.py               # 双平台评论同步
```

## 认证兼容性

| Agent | Linear | GitHub |
|-------|--------|--------|
| 所有 Agent | `$LINEAR_API_KEY`（环境变量） | `$GITHUB_TOKEN`（环境变量）或 `gh auth`（CLI） |

Skill 会自动检测可用的 GitHub 认证方式并使用，无需 Agent 专属配置。

## 技术债（待实现）

以下功能在团队 GitHub org 环境下需要实现（当前 MVP 暂缓）：

- **GitHub label 映射** — Linear label ↔ GitHub label 对应关系
- **GitHub assignee 映射** — Linear 用户 ↔ GitHub 用户名对应关系
- **GitHub Project 映射** — Linear project ↔ GitHub Project (v2) 对应关系
- **Org 级 onboarding** — 在团队 org 下发现成员/label/project，让用户选择默认值

## License

MIT

## 作者

Rachel Lu (@RachelXiaolan)
