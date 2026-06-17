# Ticket Pilot 🎫✈️

**多 Agent 通用的 Linear ↔ GitHub issue 同步 Skill。**

Ticket Pilot 让任何 AI Agent（Hermes、Claude Code、Codex、OpenClaw、Cursor、Gemini CLI）都能在处理 Linear issue 时自动与 GitHub 保持同步。当你开始处理一个 Linear issue 时，Agent 会自动：

- 在 GitHub 创建对应的镜像 issue（1:1 映射）
- 在**两个平台**同步发布进度评论（按阶段更新，不是每步都发）
- 在 Linear 上追踪状态（Linear 是唯一真相源）
- 涉及写代码时，可选创建 branch / commit / PR

## 安装

### 方式一：curl 一键安装（推荐）

```bash
# 默认装到 Claude Code
curl -fsSL https://raw.githubusercontent.com/RachelXiaolan/ticket-pilot/main/install.sh | bash

# 指定 agent（逗号分隔可装多个）
curl -fsSL https://raw.githubusercontent.com/RachelXiaolan/ticket-pilot/main/install.sh | bash -s -- --agent hermes
curl -fsSL https://raw.githubusercontent.com/RachelXiaolan/ticket-pilot/main/install.sh | bash -s -- --agent claude,codex,hermes
```

可选 agent：`claude` `codex` `hermes` `openclaw` `cursor` `gemini`

### 方式二：Claude Code 插件市场

```
/plugin marketplace add RachelXiaolan/ticket-pilot
/plugin install ticket-pilot
```

### 方式三：skills.sh CLI

```bash
npx skills add RachelXiaolan/ticket-pilot
```

### 方式四：手动安装

```bash
git clone https://github.com/RachelXiaolan/ticket-pilot.git
cp -r ticket-pilot/ ~/.claude/skills/ticket-pilot/    # 换成你的 agent 路径
```

| Agent | Skills 目录 |
|-------|------------|
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.codex/skills/` |
| Hermes | `~/.hermes/skills/productivity/` |
| OpenClaw | `~/.openclaw/skills/` |
| Cursor | `.cursor/skills/` |
| Gemini CLI | `.gemini/skills/` |

## 前置条件

### Linear
- 在 https://linear.app/settings/account/security → Personal API keys 创建个人 API key
- 设置为环境变量 `LINEAR_API_KEY`

### GitHub（三选一）
- **gh CLI**（推荐）：运行 `gh auth login`
- **Fine-grained Token**：https://github.com/settings/personal-access-tokens/new
  - Repository access：选 All repositories 或指定仓库
  - 权限勾选（都要 Read and write）：
    - **Issues** — 创建镜像 issue、加评论
    - **Contents** — branch、commit、push（有代码改动时）
    - **Pull requests** — 开 PR（可选）
    - **Metadata** — Read-only（默认必选）
  - 设置为环境变量 `GITHUB_TOKEN`
- **GitHub MCP / App**：如果已经配置过，可直接使用

### Codex 用户注意 ⚠️

Codex 默认开启沙箱，**网络是关闭的**，Linear/GitHub API 调不通。开始前把 Codex 的审批权限改为默认放行：

> Codex 设置 → Auto Review → 改为默认权限

或者命令行启动时加 flag：
```bash
codex --full-auto "用 ticket-pilot 处理 AI-2090"
```

> 其他 Agent（Hermes / Claude Code / Cursor 等）没有这个问题。

## 首次使用

首次使用 Ticket Pilot 时，Agent 会：
1. 验证 Linear + GitHub 认证
2. 自动发现你的工作区信息：team、project、label、用户
3. 让你选择默认值（team、project、label、assignee）
4. 保存到 `~/.ticket-pilot/settings.md`

之后创建 issue 时自动使用默认值。创建时直接说明即可覆盖默认值（如"在 SBY team 建个 issue"、"assign 给 Leo"）。

## 快速上手

设定完成后，只需要用自然语言告诉 Agent "我要处理这个 issue"即可触发：

```
开始做 AI-2090
```

或者更明确一点：

```
用 ticket-pilot 处理 AI-2090，我需要改 README 的安装说明
```

Agent 收到后会自动：
1. 读取 Linear issue 内容（标题、描述、当前状态）
2. 状态 → In Progress，发一条"开始"评论
3. 开始干活，在阶段节点自动发进度评论（同步到 Linear + GitHub）
4. 完成后状态 → In Review / Done，发完成评论

### 常见触发方式

| 你说的话 | Agent 会做什么 |
|---------|--------------|
| `看一下 AI-2090` / `看看这个 issue` | **只读**：读取并总结 issue 内容，不动任何东西 |
| `看看团队在做什么` | **只读**：列出队友的活跃 issue 汇总 |
| `开始做 AI-2090` | 读取 issue → In Progress → 开工 |
| `用 ticket-pilot 处理 AI-2090` | 同上，明确指定 skill |
| `AI-2090 我改完了` | 验证 → In Review → 发完成评论 |
| `AI-2090 做完了，关掉` | Done → 完成评论 |
| `建个 issue：修复登录bug` | 用你的默认 team/project/label 创建 → 同步到 GitHub |
| 不确定 | Agent 会问："你是想看一下，还是开始做？" |

> 💡 **"看一下"≠"开始做"。** Agent 不会因为你提了一个 issue 就自动改状态、建 GitHub issue。只有你明确说"开始/处理/做"才会启动完整流程。启动后，关键节点的进度评论会**自动更新**，不用你催。

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
