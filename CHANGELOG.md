# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Security
- Fix GraphQL injection risk in `scripts/sync_comment.py` — use `variables` instead of string interpolation so arbitrary comment bodies (control chars, backticks, unicode) cannot break the mutation payload.
- Fix path-traversal and missing-input-validation in `scripts/init_task_record.py`. The script previously accepted arbitrary `issue_id` and `--root` strings, so values like `../etc/passwd` or `/etc/passwd` could create task artifacts outside the intended `tasks/` directory, and whitespace / shell metacharacters could split arguments downstream. The validator now requires a strict Linear identifier format (`<TEAM_KEY>-<NUMBER>`, e.g. `AI-2134`), rejects whitespace, path separators, and shell metacharacters, and refuses to create directories whose resolved path leaves the artifact root.

### Added
- `LICENSE` file (MIT) — `SKILL.md` declared MIT but the license text was missing from the repo.
- `.gitignore` — excludes `tasks/` artifacts, local `.ticket-pilot/` settings, Python caches, OS/editor files.
- `CHANGELOG.md` — this file.
- `tests/test_init_task_record.py` — unit + argv-level tests for the input validator (whitelist / blacklist / path-traversal / shell-metacharacter rejection).

### Changed
- `SKILL.md` frontmatter `platforms`: `[linux, macos, windows]` → `[linux, macos]`. The skill relies on bash + curl + python3; on Windows it requires WSL or Git Bash, so native Windows is not officially supported.

## [3.0.0] — 2026-06

Initial public release as a multi-agent skill (`SKILL.md` + standard directory layout).

- Agent-agnostic: Claude Code, Codex, Hermes, OpenClaw, Cursor, Gemini CLI
- Linear-as-source-of-truth, GitHub as mirror
- Bidirectional comment mirroring via `scripts/sync_comment.py`
- Task artifact scaffolding via `scripts/init_task_record.py`
- Reference docs: onboarding, state model, GitHub conventions, workflow template
