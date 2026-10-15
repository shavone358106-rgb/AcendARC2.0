# AcendARC2.0
## Claude Code setup (everything-claude-code)

This repo ships the [everything-claude-code](https://github.com/WorldFlowAI/everything-claude-code) toolkit in `.claude/`, so every Claude Code session here loads it automatically:

| Folder | What it gives you |
|---|---|
| `.claude/agents/` | Subagents: planner, architect, tdd-guide, code-reviewer, security-reviewer, build-error-resolver, e2e-runner, refactor-cleaner, doc-updater |
| `.claude/commands/` | Slash commands: `/plan`, `/tdd`, `/code-review`, `/build-fix`, `/e2e`, `/verify`, `/checkpoint`, `/learn`, `/orchestrate`, `/eval`, `/refactor-clean`, `/test-coverage`, `/update-docs`, `/update-codemaps`, `/setup-pm` |
| `.claude/skills/` | Skills: backend/frontend patterns, coding standards, TDD workflow, security review, verification loop, eval harness, continuous learning, strategic compact, ClickHouse |
| `.claude/rules/` | Always-on rules: security, coding style, testing, git workflow, agents, hooks, patterns, performance |
| `.claude/contexts/` | Mode prompts: dev, review, research |
| `.claude/settings.json` | Active hooks: session memory, compaction suggestions, JS/TS format/typecheck/console.log checks |
| `.claude/scripts/`, `.claude/tests/` | Hook scripts and their tests (`node .claude/tests/run-all.js`) |

Reference material (MCP server templates, example CLAUDE.md files, setup guide) is in `docs/everything-claude-code/`.
