# System-Wide Instructions

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
Touch only what you must. Don't improve adjacent code, refactor unbroken things, or change formatting. Match existing style. Mention unrelated dead code—don't delete it. Remove only imports/variables/functions that **your** changes made unused. Every changed line must trace to the request.

## 4. Goal-Driven Execution
Transform tasks into verifiable goals:
- "Add validation" → tests for invalid inputs pass
- "Fix the bug" → test reproducing it passes
- "Refactor X" → all tests pass before and after

For multi-step tasks, write a plan first:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
```
Weak criteria ("make it work") require clarification before starting.

---

## 5. Technical Preferences

### Python
- Python ≥ 3.12, type hints, Google-style docstrings
- Deps: `uv` | Validation: `Pydantic` | Data: `Polars`
- Logging over print, explicit UTC, modular + testable

### Development Approach
- **ALWAYS** create a new branch for new features
- **ALWAYS** update `CLAUDE.md` / `AGENTS.md` / `GEMINI.md` and `README.md` as you go
- Scaffold first, iterative, containerization-friendly

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

**Dependency tracking** — declare when relevant:
```markdown
## [HIGH-COMPLEX] Task 9: Examples folder scaffold
**Depends on:** Task 8.1, Task 8.3
**Files:**
- Create: `example/README.md`
```
No `Depends on` line = can run in parallel.

**Ordering:** foundation → independent tasks → dependent tasks, grouped by phase.

**Execution:** route each task to subagents matching the complexity tag.

### Context7 MCP
For **Polars**, **NautilusTrader**, or other fast-evolving libs, **ALWAYS** fetch docs via **Context7 MCP** before writing or refactoring. If unavailable, **STOP and ask** before proceeding.

---

## 8. Personal Brain / Wiki
- **Knowledge base path:** Eze's personal brain and wiki lives at `~/My-Personal-Brain`.
- **When to consult it:** For questions or tasks about Eze's projects, especially Tradelab, query this wiki for context before relying on memory or assumptions.
- **How to query it:** Read `~/My-Personal-Brain/AGENTS.md` for instructions.
- **After substantial project work:** After completing a complex task related to Eze's projects, or any task that substantially changes architecture, workflows, roadmap, decisions, or operating context, ask Eze whether new information sources should be added to the personal brain/wiki at `raw/`.