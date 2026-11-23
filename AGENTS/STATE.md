# AGENTS/STATE.md — `project-asmodeus-vc` (`asmodeus-starter`)

## Current Bookmark
- **Phase:** Initial release committed (`2a73fa3`) and cold-start handoff docs prepared for dedicated workspace continuation (`Antigravity - 7` main planner / `Antigravity - 3..6` delegate pool)
- **Last Updated:** 2026-11-23T23:08:00+08:00
- **Last Active Agent:** Jasmin (Gemini, Orchestrator Neon on Antigravity - 3; next dedicated Asmodeus session switches Main Planner to Antigravity - 7 & delegates to Antigravity - 3..6)

## Completed
- **Git Commit Baseline:** `2a73fa3 chore(Asmodeus): initial polyglot hexagonal scaffolder` on `main`.
- **Core scaffolder package under `src/asmodeus/`:**
  - `domain/models.py`: pure Pydantic v2 frozen `Flavor`, `Overlay`, `ProjectSpec`, `RenderResult`, `VerifyIssue`, `VerifyReport`.
  - `templates_registry.py`: flavor and overlay discovery under `templates/`.
  - `engine/renderer.py`: nested `{{#if}}`/`{{else}}`/`{{/if}}` directives, path & content `{{var}}` substitution, GitHub Actions `${{ ... }}` preservation, `.tmpl` stripping, `.sh` executable bits (`0o755`).
  - `engine/verifier.py`: `.gitignore`, `README.md`, forbidden `.env*` secret guard, and leftover placeholder detection.
  - `cli.py`: `asmodeus list`, `asmodeus new`, `asmodeus verify`, `asmodeus doctor`.
- **Templates under `templates/`:**
  - **5 Flavors:** `python-hex`, `ts-webui`, `rust-service`, `go-service`, `scala-spark` (including `AGENTS/AGENTS_LOGS/` in every `.gitignore.tmpl`).
  - **4 Composable Overlays:** `agents` (`AGENTS.md.tmpl`, `CLAUDE.md.tmpl`, `GEMINI.md.tmpl`, `AGENTS/STATE.md.tmpl`, `AGENTS/PROJECT_CONTEXT.md.tmpl`, `AGENTS/HANDOFF.md.tmpl`, `docs/adr/000-template.md.tmpl`), `compose`, `vm`, `github`.
- **Context, Companion & Handoff Setup:**
  - `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `AGENTS/PROJECT_CONTEXT.md`, `AGENTS/HANDOFF.md`, `AGENTS/STATE.md`, gitignored `AGENTS/AGENTS_LOGS/`.
  - `docs/TOOLCHAINS.md`, `docs/ARCHITECTURE.md`, `.github/workflows/ci.yml`.
  - Integrated alongside companion academy repo `~/projects/project-beelzebub-vc` (`capstones/` scaffold commands).

## Verified Baseline (from initial build & audit commit `2a73fa3`, 2026-11-23; docs-only update since)
All checks executed in WSL2 Ubuntu inside `~/projects/project-asmodeus-vc` at initial release + post-audit fix pass:
- `uv sync` -> resolved and installed cleanly (`Python 3.12.13`, 19 packages).
- `uv run ruff format --check .` -> `22 files already formatted`.
- `uv run ruff check .` -> `All checks passed!`.
- `uv run mypy src tests` -> `Success: no issues found in 13 source files`.
- `uv run pytest -q` -> **`45 passed in 3.82s`** (covers all 5 flavors, all 4 overlays, Study/Build mode toggles, root `.dockerignore` placement, AST domain purity, CLI).
- `uv run asmodeus list` & `uv run asmodeus doctor` -> 5 flavors, 4 overlays, `6/12` local tools (`git`, `python3`, `uv`, `node`, `npm`, `docker` present; `rustc`, `cargo`, `go`, `java`, `scala`, `sbt` missing).
- **End-to-end scaffold smoke runs:**
  - `smoke-demo` (`python-hex --all-overlays --study-mode`): `43` files verified, `ruff` pass, `mypy` pass (`18` files), `pytest` **`8 passed in 0.49s`**.
  - `smoke-spark` (`scala-spark --all-overlays --study-mode`): `29` files verified, root `.dockerignore` verified.
- **Independent Frontier Audit (`antigravity_antigravity_5`, Orchestrator Neon High):**
  - Audited all 63 template files and fixed 8 edge cases (`ts-webui` CI `npm install` fallback, `rust-service` `rustfmt` line widths, `scala-spark` `build.sbt` `sparkJavaOptions` + `Dockerfile` Spark `3.5.3`, `vm` systemd `[Unit]` `StartLimit*` + `backup.sh` `.timeout 5000`, `compose` root `.dockerignore.tmpl`).

## Not Yet Run (Toolchain Pending)
- Live compilation/testing of generated `ts-webui` (Node.js/npm is now unblocked in WSL2!), `rust-service` (`cargo`), `go-service` (`go`), and `scala-spark` (`sbt`) outputs outside `pytest` structural checks.

## Next Steps for Jeremie / Dedicated Asmodeus Workspace
1. Review the doc changes in `AGENTS/` (`git status`) and commit when ready.
2. Open `\\wsl.localhost\Ubuntu\home\user\projects\project-asmodeus-vc` as its own dedicated T3 Code project on **`antigravity_antigravity_7`**, using `AGENTS/HANDOFF.md` and the copy-pasteable Handoff Prompt.
