# `project-asmodeus-vc` — Project Context & Architecture Reference

## 1. Purpose

**Asmodeus** (`asmodeus-starter`) is Jeremie's permanent polyglot hexagonal project scaffolder and force-multiplier starter kit. It lets him spin up production-structured Python, TypeScript WebUI, Rust, Go, and Scala/Spark projects in seconds -- complete with composable overlays (`agents`, `compose`, `vm`, `github`) and a **Study Mode vs Build Mode** toggle (`--study-mode`) matching his *OLYMPUS* / *Mammon* engineering standards.

**Companion Project (`~/projects/project-beelzebub-vc`):** **Beelzebub v2** (interactive 8-Unit / 42-Chapter Engineering Academy & Sandbox) includes capstone missions whose `asmodeusScaffoldCmd` fields invoke `asmodeus new ...` to bootstrap clean starter workspaces.

---

## 2. Core Codebase Map

- **`src/asmodeus/domain/models.py` (PURE — zero I/O):**
  - `Flavor` (`python-hex`, `ts-webui`, `rust-service`, `go-service`, `scala-spark`)
  - `Overlay` (`agents`, `compose`, `vm`, `github`)
  - `ProjectSpec` (validates kebab-case slug `^[a-z][a-z0-9-]{1,48}$`; derives `package_name`, `crate_name`, `pascal_name`, `go_module`, `scala_package`, `template_context()`, and `condition_flags()`).
  - `RenderResult`, `VerifyIssue`, `VerifyReport`.
- **`src/asmodeus/templates_registry.py`:** Resolves `templates/flavors/<flavor>` and `templates/overlays/<overlay>`.
- **`src/asmodeus/engine/renderer.py`:**
  - Evaluates line-based conditionals (`{{#if <flag>}}`, `{{else}}`, `{{/if}}`) for `study_mode`, `with_compose`, `with_vm`, `with_agents`, `with_github`.
  - Substitutes `{{var}}` in BOTH file paths and file contents for `project_name`, `package_name`, `crate_name`, `pascal_name`, `go_module`, `scala_package`, `description`, `author`, `github_user`, `year`.
  - Preserves GitHub Actions `${{ ... }}` expressions using negative lookbehind `(?<!\$)\{\{([^{}]+)\}\}`.
  - Strips `.tmpl` suffix on render, copies non-`.tmpl` files verbatim, sets `.sh` files executable (`0o755`), and rejects non-empty targets unless `--force`.
- **`src/asmodeus/engine/verifier.py`:** Verifies `.gitignore`, `README.md`, absence of `.env*` secrets (allowing `.env.example` / `.env.compose.example`), and zero unrendered `{{...}}` tokens.
- **`src/asmodeus/cli.py`:** `asmodeus list`, `asmodeus new`, `asmodeus verify`, `asmodeus doctor`.
- **`templates/flavors/*` & `templates/overlays/*`:** All 5 base templates + 4 overlays.
- **`docs/TOOLCHAINS.md` & `docs/ARCHITECTURE.md`:** WSL2 toolchain setup and boundary guide.
- **`tests/`:** `test_models.py`, `test_renderer.py`, `test_scaffold_all_flavors.py`, `test_code_boundaries.py`.

---

## 3. Non-Negotiable Invariants
1. **Pure Domain Layer:** `src/asmodeus/domain/` must never import `os`, `pathlib`, `sys`, `subprocess`, `shutil`, `json`, `urllib`, `httpx`, `sqlite3`, or call `datetime.now()` (enforced by `tests/test_code_boundaries.py`).
2. **Template Token Strictness:** Every template directive/variable must belong to the exact allowed set; never emit unescaped non-GHA `{{...}}` in rendered files.
3. **4-Hop Hygiene:** Keep CLI -> Domain -> Engine/Registry -> Filesystem layering clean.
4. **Git & Log Hygiene:** Jeremie commits/pushes manually; agents write new immutable session logs under gitignored `AGENTS/AGENTS_LOGS/` and update tracked `AGENTS/STATE.md` / `AGENTS/HANDOFF.md`.
5. **Persona & Formatting:** Jasmin persona uses **kaomojis ONLY — zero emojis** across user responses and documentation.
6. **Antigravity Account Routing Rule:** NEVER use Account #1 (`Antigravity`) or Account #2 (`Antigravity - 2`). Keep main planner/session on **Account #7 (`antigravity_antigravity_7`)** and delegate subagents exclusively to **Accounts #3–6 (`antigravity_antigravity_3`..`6`)**, prioritizing #5 and #6 first.
7. **PowerShell -> WSL Quoting Rule:** When calling `wsl -e bash -lc '...'` from Windows PowerShell, NEVER embed double quotes `"`, unquoted parens `()`, or pipes `|` inside the single-quoted bash string.

---

## 4. Mandatory Quality Gates (WSL2 Ubuntu)
```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest -q
```
