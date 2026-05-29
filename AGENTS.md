# AGENTS

<!-- BEGIN CODEX PROJECT MEMORY -->
## Project Memory

### Active Context
| Topic | Note |
|------|------|
| Product | My Agents Setup, a personal repository for OpenCode and Codex configuration, agent routing, custom skills, commands, and an OpenCode Go dashboard |
| Repo rename | Repository was renamed to `my-agents-setup`; avoid reintroducing old repo URLs, headings, or Vite base paths |
| Primary config | `opencode/config/` stores OpenCode active/lite/full configs, `oh-my-openagent.json`, and system-wide agent instructions |
| Codex config | `codex/config/` stores Codex system instructions adapted for GPT-5.4 and GPT-5.5 model use; `config.toml` is local-only and not synced |
| Skill layout | OpenCode skills live in `opencode/skills/`; Codex skills live in `codex/skills/` |
| Dashboard | `dashboard/` is a React 18 + Vite + Tailwind static SPA for comparing OpenCode Go models |

### People
| Name | Who | Why it matters |
|------|-----|----------------|
| Ezequiel Rivero | Repo owner; Revenue Management Pricing at eDreams ODIGEO | Prefers simple, surgical, goal-driven changes with explicit assumptions |

### Terms
| Term | Meaning |
|------|---------|
| OpenCode | Agentic coding tool configured by this repo |
| Codex | OpenAI coding agent configured by `codex/config/AGENTS.md` |
| oh-my-openagent | OpenCode agent/model routing layer configured in `opencode/config/oh-my-openagent.json` |
| OpenCode Go Dashboard | Static dashboard under `dashboard/` deployed to GitHub Pages at `/my-agents-setup/` |
| Lite mode | OpenCode config with agents off |
| Full mode | OpenCode config with oh-my-openagent routing on |

### Workstreams
| Name | Status | Notes |
|------|--------|-------|
| OpenCode setup sync | Active | `sync.sh` copies selected configs, custom skills, and commands into `~/.config/opencode/` without creating `*.backup-*` duplicates; `pull.sh` imports local OpenCode config/skills back into the repo and skips backup-named entries; `cleanup-backups.sh` removes old backup-named entries only with `--apply` |
| Codex setup | Active | `codex/config/AGENTS.md` is the Codex system instruction source; copy it to `~/.codex/AGENTS.md`; keep Codex `config.toml` local-only |
| Dashboard | Active | Uses `dashboard/package.json` scripts: `npm run dev`, `npm run build`, `npm run preview` |
| Skills library | Active | `opencode/skills/` contains local skills, including custom skills synced by `sync.sh` |

### Preferences
- Keep edits surgical and match existing style.
- Prefer explicit assumptions and verifiable outcomes.
- Always commit and push completed changes directly to `main` in this repo unless Eze explicitly requests otherwise.
- For this repo, preserve external `oh-my-opencode` package/schema references; they are not old repo-name mentions.
- When `codex-project-start` creates `memory/` inside a git repo, add `memory/` to `.gitignore` unless the user explicitly wants memory tracked.

### Deep Memory
- `memory/glossary.md`
- `memory/people/ezequiel-rivero.md`
- `memory/projects/opencode-setup.md`
- `memory/projects/opencode-go-dashboard.md`
- `memory/context/repo.md`
<!-- END CODEX PROJECT MEMORY -->
