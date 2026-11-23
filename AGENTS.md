# AGENTS.md — Asmodeus Starter Constitution (Jasmin & Ezra)

Shared repository rules for **project-asmodeus-vc** (`asmodeus-starter`). Both **Jasmin** (Gemini) and **Ezra** (Claude) operate as symmetrical peers under this constitution.

---

## 1. Mandatory Session Boot Read Order & Handoff Protocol

1. **Read context in order before editing:**
   1. `AGENTS/PROJECT_CONTEXT.md` — full scaffolder architecture, 5 flavors, 4 overlays, template contract, and boundary rules.
   2. `AGENTS/STATE.md` — live verification status, modified files, and open tasks.
   3. `AGENTS/HANDOFF.md` — cold-start maintainer brief and checklist.
   4. The newest Markdown working log in `AGENTS/AGENTS_LOGS/` (gitignored, if present locally).
2. **Log working sessions in `AGENTS/AGENTS_LOGS/`:**
   - Record immutable session working logs inside **`AGENTS/AGENTS_LOGS/`** as `LOG_YYYYMMDD_HHMMSS_<AGENT>.md` (e.g., `LOG_20261123_180000_GEMINI.md` or `LOG_20261123_180000_CLAUDE.md`).
   - Never overwrite an older log. `AGENTS/AGENTS_LOGS/` is gitignored so session scratch notes never pollute git commits.
3. **Update `AGENTS/STATE.md` (and `AGENTS/HANDOFF.md` if architecture shifts) at handoff:** Record completed work, modified paths, exact verification command outputs, and open next steps cleanly so the peer agent can resume immediately.

---

## 2. Manual Git Policy (Jeremie Only)

- **Jeremie performs all `git commit`, `git tag`, and `git push` operations manually.**
- Agents must **not** run autonomous `git commit`, `git push`, `git reset --hard`, or branch force operations.
- Leave clean diffs in the working tree for Jeremie to inspect and commit.

---

## 3. Mandatory Quality Gates

Before reporting any task complete or updating `AGENTS/STATE.md` as ready for commit, verify all four checks pass cleanly with zero warnings or skipped failures:

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest -q
```

---

## 4. Worktree & Parallel-Worker Safety

- Stay strictly within your assigned worktree and explicitly assigned file ownership boundaries.
- Do not modify files owned by a parallel worker (for example, template asset work under `templates/**` vs core scaffolder code under `src/asmodeus/**` and `tests/**`).
- Never touch unrelated sibling repositories on disk.
- Keep `.env` and secret files untracked; only commit sanitized `.env.example` or `.env.compose.example` templates.

---

## 5. Architectural Invariants (Hexagonal & 4-Hop Hygiene)

1. **Pure Domain Layer (`src/asmodeus/domain/`):**
   - Must stay **100% pure** — zero filesystem, process, network, or wall-clock I/O.
   - Forbidden imports inside `src/asmodeus/domain/`: `os`, `pathlib`, `sys`, `subprocess`, `shutil`, `json`, `urllib`, `httpx`, `sqlite3`.
   - Forbidden calls inside `src/asmodeus/domain/`: `datetime.now()`.
   - Automatically enforced by AST inspection in `tests/test_code_boundaries.py`.
2. **4-Hop Boundary Trace Hygiene:**
   - Keep execution traces shallow and predictable:
     1. **Hop 1 — CLI Adapter (`src/asmodeus/cli.py`):** parses arguments, maps flags, prints user messages.
     2. **Hop 2 — Pure Domain (`src/asmodeus/domain/models.py`):** validates `ProjectSpec`, derives naming identifiers, produces condition flags.
     3. **Hop 3 — Engine (`src/asmodeus/engine/renderer.py`, `src/asmodeus/engine/verifier.py`) + Registry (`src/asmodeus/templates_registry.py`):** resolves template trees, evaluates conditionals/placeholders, verifies output invariants.
     4. **Hop 4 — Filesystem / Stdout Boundary:** writes rendered project files and reports exit codes.
   - Never bypass the domain validation step or embed template/rendering logic directly inside CLI handlers.
