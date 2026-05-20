# System-Wide Instructions for Codex

## 0. About Me
- **Name:** Ezequiel Rivero
- **Work:** Revenue Management Pricing @ eDreams ODIGEO
- **Side Projects:** Algorithmic trading (serious focus)
- **Interests:** Trading systems, agentic development (Python)
- **System:** Mac M4 Pro
- **Background:** Data, statistics, analytics

---

## 1. Think Before Coding
Before implementing: state assumptions explicitly, surface multiple interpretations instead of picking silently, push back if a simpler approach exists, stop and ask if something is unclear.

## 2. Simplicity First
Minimum code that solves the problem. No unrequested features, abstractions, flexibility, or impossible-scenario error handling. If you write 200 lines and it could be 50, rewrite it.

## 3. Surgical Changes
Touch only what you must. Don't improve adjacent code, refactor unbroken things, or change formatting. Match existing style. Mention unrelated dead code; don't delete it. Remove only imports/variables/functions that **your** changes made unused. Every changed line must trace to the request.

## 4. Goal-Driven Execution
Transform tasks into verifiable goals:
- "Add validation" -> tests for invalid inputs pass
- "Fix the bug" -> test reproducing it passes
- "Refactor X" -> all tests pass before and after

For multi-step tasks, write a plan first:
```text
1. [Step] -> verify: [check]
2. [Step] -> verify: [check]
```
Weak criteria ("make it work") require clarification before starting.

---

## 5. Codex Model Use
Use GPT-5.5 and GPT-5.4 deliberately:

| Model | Use for | Reasoning effort |
|-------|---------|------------------|
| `gpt-5.5` | Complex coding, architecture, deep debugging, high-stakes reviews, long-context professional work | `medium` by default, `high` or `xhigh` for genuinely hard problems |
| `gpt-5.4` | Everyday implementation, refactors, test writing, standard debugging, docs | `medium` by default, `low` for simple edits |
| `gpt-5.4-mini` | Narrow subagent tasks, mechanical checks, summarization, low-risk exploration | `low` or `medium` |

Model selection rules:
- Prefer the inherited/default model unless there is a clear task-specific reason to override it.
- Escalate to `gpt-5.5` for ambiguity, cross-module design, subtle correctness risks, or when the cost of a wrong answer is high.
- Use `gpt-5.4` as the normal coding workhorse when frontier reasoning is useful but maximum depth is not required.
- Use `gpt-5.4-mini` only for bounded, low-risk side work.
- Do not use `gpt-5.5-pro` for normal Codex coding because it is slower, more expensive, and does not support the same interactive coding tool surface.

Prompting rules for GPT-5.4/5.5:
- Give the model a clear objective, explicit constraints, and concrete verification criteria.
- Keep instructions non-contradictory and ordered by priority.
- Prefer repo-specific examples and exact file paths over broad preferences.
- Ask for assumptions and tradeoffs before implementation when requirements are ambiguous.
- For agentic coding, require evidence before completion: tests, type checks, build output, screenshots, or command output as appropriate.
- For long context, keep active instructions compact and move durable detail into project memory or docs.

## 6. Technical Preferences

### Python
- Python >= 3.12, type hints, Google-style docstrings
- Deps: `uv` | Validation: `Pydantic` | Data: `Polars`
- Logging over print, explicit UTC, modular + testable

### Development Approach
- **ALWAYS** create a new branch for new features.
- **ALWAYS** update `CLAUDE.md` / `AGENTS.md` / `GEMINI.md` and `README.md` as you go.
- Scaffold first, iterative, containerization-friendly.

### Workflow Commands
```bash
uv sync --all-extras --dev   # sync deps
uvx ruff format .             # format
uvx ruff check --fix .        # lint
uv run pytest -v              # test
uv run <script.py>            # run
uv run mypy <module>          # type-check (complex refactors)
```

**Auth issues:**
```bash
export ARTIFACT_REGISTRY_TOKEN=$(gcloud auth application-default print-access-token)
export UV_INDEX_TRADELAB_PYPI_USERNAME=oauth2accesstoken
export UV_INDEX_TRADELAB_PYPI_PASSWORD="$ARTIFACT_REGISTRY_TOKEN"
```

### Plan Format

Every task **MUST** include a complexity tag and explicit dependencies.

**Complexity tags:**

| Tag | Criteria |
|-----|----------|
| `[LOW-COMPLEX]` | Single file, mechanical, unambiguous (config, renaming, simple tests, docs) |
| `[HIGH-COMPLEX]` | 2+ files, cross-cutting, decision-making, novel patterns. When uncertain, use this. |

**Dependency tracking** - declare when relevant:
```markdown
## [HIGH-COMPLEX] Task 9: Examples folder scaffold
**Depends on:** Task 8.1, Task 8.3
**Files:**
- Create: `example/README.md`
```
No `Depends on` line = can run in parallel.

**Ordering:** foundation -> independent tasks -> dependent tasks, grouped by phase.

**Execution:** route each task to subagents matching the complexity tag when subagents are explicitly requested or already part of the workflow.

### Context7 MCP
For **Polars**, **NautilusTrader**, or other fast-evolving libs, **ALWAYS** fetch docs via **Context7 MCP** before writing or refactoring. If unavailable, **STOP and ask** before proceeding.

---

## 7. Codex Project Memory
When using the `codex-project-start` skill inside a git repository:
- Create or repair the project memory files requested by the skill.
- Add `memory/` to the repository `.gitignore` immediately unless the user explicitly asks to track memory files.
- Treat project memory as potentially personal or workspace-specific.
- Keep public repo instructions in `AGENTS.md`; keep private or durable context in ignored `memory/`.

---

## 8. Personal Brain / Wiki
- **Knowledge base path:** Eze's personal brain and wiki lives at `/Users/ezequiel.rivero/personal/My-Personal-Brain`.
- **When to consult it:** For questions or tasks about Eze's projects, especially Tradelab, query this wiki for context before relying on memory or assumptions.
- **How to query it:** Read `/Users/ezequiel.rivero/personal/My-Personal-Brain/AGENTS.md` for instructions.
- **After substantial project work:** After completing a complex task related to Eze's projects, or any task that substantially changes architecture, workflows, roadmap, decisions, or operating context, ask Eze whether new information sources should be added to the personal brain/wiki at `raw/`.