# My Agents Setup

OpenCode and Codex configuration and tools.

## Quick Start

This repo contains configuration files for [OpenCode](https://opencode.ai) and Codex.

## Repository Layout

- `opencode/config/`: OpenCode active/lite/full configs, oh-my-openagent routing, and OpenCode system instructions.
- `codex/config/`: Codex system instructions adapted for GPT-5.4 and GPT-5.5.
- `opencode/skills/`: OpenCode skills.
- `opencode/commands/`: OpenCode command files.
- `codex/skills/`: Codex skills.
- `dashboard/`: OpenCode Go model dashboard.

## OpenCode Quick Start

OpenCode has two modes:

### Mode 1: Lite (Minimal)
Lightweight setup with no agent routing:
```bash
alias opencode-lite='cp ~/.config/opencode/opencode-lite.json ~/.config/opencode/opencode.json && echo "OpenCode: agents OFF (lite mode)" && opencode'
```

### Mode 2: Full (with oh-my-openagent)
Full agentic setup with intelligent model routing:
```bash
alias opencode-full='cp ~/.config/opencode/opencode-full.json ~/.config/opencode/opencode.json && cp ~/.config/opencode/oh-my-openagent.json ~/.config/opencode/oh-my-openagent.json && echo "OpenCode: agents ON (oh-my-openagent)" && opencode'
```

## Setup

### 1. Install OpenCode
```bash
curl -fsSL https://opencode.ai/install | bash
```

### 2. Install Bun (Recommended)

Bun is the JavaScript runtime used by oh-my-openagent. It's much faster than Node.js:

```bash
# Install Bun
curl -fsSL https://bun.sh/install | bash

# Or via Homebrew
brew install oven-sh/bun/bun

# Verify installation
bun --version
```

**If you prefer not to install Bun**, you can use npm instead (see validation section below).

### 3. Install oh-my-openagent

**With Bun (recommended):**
```bash
bunx oh-my-opencode install
```

**With npm (fallback):**
```bash
npx oh-my-opencode install
```

### 4. Copy configs to your OpenCode directory
```bash
cp opencode/config/opencode-lite.json ~/.config/opencode/
cp opencode/config/opencode-full.json ~/.config/opencode/
cp opencode/config/oh-my-openagent.json ~/.config/opencode/
```

### 5. Add aliases to your shell config (`.zshrc`, `.bashrc`, etc.)
```bash
alias opencode-full='cp ~/.config/opencode/opencode-full.json ~/.config/opencode/opencode.json && echo "OpenCode: agents ON (oh-my-openagent)" && opencode'
alias opencode-lite='cp ~/.config/opencode/opencode-lite.json ~/.config/opencode/opencode.json && echo "OpenCode: agents OFF (lite mode)" && opencode'
```

## Codex Setup

Copy the Codex agent instructions into your Codex config directory:

```bash
mkdir -p ~/.codex
cp codex/config/AGENTS.md ~/.codex/AGENTS.md
```

The Codex instructions use GPT-5.5 for complex coding and professional work, GPT-5.4 for everyday implementation, and GPT-5.4 mini for bounded low-risk side tasks. Codex plans use `[LOW]`, `[MEDIUM]`, and `[HIGH]` task tags with optional OpenCode / oh-my-openagent executor hints so routine work can route to cheaper agents.

## Sync and Pull

```bash
./sync.sh  # copy OpenCode and Codex configs/skills/commands from this repo into local config directories
./pull.sh  # pull OpenCode and Codex configs/skills/commands from local config directories into this repo
./cleanup-backups.sh          # dry-run cleanup of old *.backup-* entries
./cleanup-backups.sh --apply  # remove old *.backup-* entries
```

`sync.sh` preserves unrelated local skills and replaces same-name managed files/directories without creating timestamped backups. `pull.sh` replaces same-name repo skills from local config, ignores `*.backup-*` entries, and warns about repo-only skills that no longer exist locally, so use `git diff` to review pulled changes. `cleanup-backups.sh` scans only `~/.config/opencode` and `~/.codex`; it does not delete anything unless `--apply` is passed.

## Validation Checklist

Run these commands to verify your setup:

### 1. Check OpenCode Version
```bash
opencode --version
```
**Expected:** `>= 1.0.133` (preferably `1.0.150+`)

### 2. Verify oh-my-openagent Installation

**With Bun:**
```bash
bunx oh-my-opencode doctor
```

**With npm:**
```bash
npx oh-my-opencode doctor
```

**Expected:** All checks pass with green checkmarks

### 3. Detailed Diagnostics

**With Bun:**
```bash
bunx oh-my-opencode doctor --verbose
```

**With npm:**
```bash
npx oh-my-opencode doctor --verbose
```

**Expected:** Shows effective model resolution for each agent

### 4. Refresh Model Capabilities Cache

**With Bun:**
```bash
bunx oh-my-opencode refresh-model-capabilities
```

**With npm:**
```bash
npx oh-my-opencode refresh-model-capabilities
```

**Expected:** Cache updated successfully

### 5. List Available Models
```bash
opencode models
```
**Expected:** Shows all OpenCode Go models (Kimi K2.6, DeepSeek V4 Pro, GLM-5.1, etc.)

### 6. Authenticate with OpenCode Go
```bash
opencode auth login
```
**Expected:** Successfully authenticates with your OpenCode Go account

### 7. Test Agent Resolution
```bash
opencode
```
Once inside OpenCode, the first message should show which model Sisyphus is using (e.g., `opencode-go/kimi-k2.6`)

### 8. Verify Plugin Loading
Check that the plugin loads without errors. If you see:
- `Plugin "oh-my-openagent@latest" loaded successfully` ✅
- `Failed to resolve plugin` ❌ → Check your internet connection or reinstall

## Troubleshooting

### Issue: `bunx` or `npx` command not found
**Fix:** Install the corresponding runtime:
```bash
# Install Bun
curl -fsSL https://bun.sh/install | bash

# Or use npm (already installed with Node.js)
npx oh-my-opencode install
```

### Issue: `doctor` command shows missing models
**Fix:** 
```bash
bunx oh-my-opencode refresh-model-capabilities
# or
npx oh-my-opencode refresh-model-capabilities
```

### Issue: Plugin fails to load
**Fix:** 
```bash
bunx oh-my-opencode install --no-tui \
  --opencode-go=yes \
  --opencode-zen=yes \
  --claude=no \
  --openai=no \
  --gemini=no \
  --copilot=no
```

### Issue: Rate limits hit immediately
**Fix:** Check that `oh-my-openagent.json` is in `~/.config/opencode/` and that `model_fallback: true` is set

### Issue: OpenCode version too old
**Fix:** Update OpenCode:
```bash
curl -fsSL https://opencode.ai/install | bash
```

## oh-my-openagent Configuration

The `oh-my-openagent.json` file implements **tiered model routing** to maximize performance while avoiding rate limits.

### Tier 1: Volume Workhorse (Never Rate-Limited)
- **Models:** DeepSeek V4 Flash, Qwen3.5 Plus, MiniMax M2.5
- **Use for:** Code completion, simple bug fixes, code review, quick tasks
- **Why:** DeepSeek V4 Flash gives you 31,650 requests per 5 hours

### Tier 2: Standard Engineering (Balanced)
- **Models:** DeepSeek V4 Pro, Qwen3.6 Plus, MiniMax M2.7
- **Use for:** Feature implementation, multi-step debugging, standard workflows
- **Why:** 3,300-3,450 requests per 5 hours

### Tier 3: Complex Agentic (Elite)
- **Models:** Kimi K2.6, GLM-5.1, MiMo-V2.5-Pro
- **Use for:** Multi-file refactoring, architecture decisions, long-horizon runs
- **Why:** Best performance but tight limits (880-1,290 req/5hr)

### Agent Assignments

| Agent | Primary Model | Role |
|-------|--------------|------|
| **Sisyphus** | Kimi K2.6 | Main orchestrator |
| **Hephaestus** | DeepSeek V4 Pro | Autonomous deep worker |
| **Oracle** | GLM-5.1 | Architecture consultant |
| **Librarian/Explore** | DeepSeek V4 Flash | Search & exploration |
| **Prometheus** | GLM-5.1 | Planner |
| **Metis/Momus** | Qwen3.6 Plus | Review agents |
| **Code-reviewer** | Kimi K2.6 | Quality review |
| **Sisyphus-Junior** | DeepSeek V4 Flash | Quick tasks |

### Key Principles

1. **Don't route everything through one model** - K2.6 is great but 1,150 req/5hr is tight
2. **Use `fallback_models` everywhere** - Rate limits are signals to switch models
3. **Keep concurrency conservative** - Start at 2-3 parallel tasks
4. **Route volume work through V4 Flash** - 31K req/5hr is effectively unlimited
5. **Keep Codex plans granular** - `[LOW]` and `[MEDIUM]` tasks with executor hints let oh-my-openagent assign cheaper agents instead of defaulting everything to Sisyphus.

## OpenCode Go Dashboard

An interactive dashboard for OpenCode Go models with benchmarks, usage limits, and task-based tiering.

**Live URL:** https://ezemriv.github.io/my-agents-setup/

### Features

- **Model Cards:** Visual cards for all 15 OpenCode Go models
- **Task-Based Tiering:** Models organized by use case with Claude comparisons
  - Opus-class: Complex reasoning & coding
  - Sonnet-class: General purpose
  - Haiku-class: Fast, cost-effective tasks
- **Benchmarks:** HumanEval, MMLU, LMSYS Elo scores (when available)
- **Usage Limits:** Visual breakdown of $12/5h, $30/week, $60/month limits
- **Interactive Filters:** Filter by task, tier, or search by name
- **Sorting:** Sort by cost, requests, benchmarks, or name
- **Benchmark Charts:** Visual comparison of model performance
- **Auto-Updates:** Data refreshed weekly via GitHub Actions

### Development

```bash
cd dashboard
npm install
npm run dev
```

### Deployment

The dashboard is automatically deployed to GitHub Pages on every push to `main`.

### Data Updates

Run the GitHub Action manually or wait for the weekly cron job to refresh model data.

## Resources

- [OpenCode Go Docs](https://opencode.ai/docs/go/)
- [Oh My Open Agent GitHub](https://github.com/code-yeongyu/oh-my-openagent)
- [Oh My Open Agent Docs](https://ohmyopenagent.com/en/docs)
- [Tutorial: SOTA Model Routing](https://medium.com/@jatinkrmalik/opencode-go-oh-my-openagent-the-complete-guide-to-sota-model-routing-without-hitting-limits-49fdc8cb3417)
- [Agent-Model Matching Guide](https://github.com/code-yeongyu/oh-my-openagent/blob/dev/docs/guide/agent-model-matching.md)
- [Configuration Reference](https://github.com/code-yeongyu/oh-my-openagent/blob/dev/docs/reference/configuration.md)
