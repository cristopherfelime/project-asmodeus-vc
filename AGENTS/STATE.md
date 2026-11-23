# AGENTS/STATE.md — `project-asmodeus-vc` (`asmodeus-starter`)

## Current Bookmark
- **Phase:** Initial release audited, patched, re-verified, and ready for first manual commit by Jeremie
- **Last Updated:** 2026-11-23T18:10:00+08:00
- **Last Active Agent:** Jasmin (Gemini, Orchestrator Neon)

## Completed
- Core scaffolder package under `src/asmodeus/`:
  - `domain/models.py`: pure Pydantic v2 frozen `Flavor`, `Overlay`, `ProjectSpec`, `RenderResult`, `VerifyIssue`, `VerifyReport`.
  - `templates_registry.py`: flavor and overlay discovery under `templates/`.
  - `engine/renderer.py`: nested `{{#if}}`/`{{else}}`/`{{/if}}` directives, path & content `{{var}}` substitution, GitHub Actions `${{ ... }}` preservation, `.tmpl` stripping, `.sh` executable bits (`0o755`).
  - `engine/verifier.py`: `.gitignore`, `README.md`, forbidden `.env*` secret guard, and leftover placeholder detection.
  - `cli.py`: `asmodeus list`, `asmodeus new`, `asmodeus verify`, `asmodeus doctor`.
- Templates under `templates/`:
  - **5 Flavors:** `python-hex`, `ts-webui`, `rust-service`, `go-service`, `scala-spark` (including `AGENTS/AGENTS_LOGS/` in every `.gitignore.tmpl`).
  - **4 Composable Overlays:** `agents` (`AGENTS.md.tmpl`, `CLAUDE.md.tmpl`, `GEMINI.md.tmpl`, `AGENTS/STATE.md.tmpl`, `AGENTS/PROJECT_CONTEXT.md.tmpl`, `AGENTS/HANDOFF.md.tmpl`, `docs/adr/000-template.md.tmpl`), `compose`, `vm`, `github`.
- Context & Maintainer Setup:
  - `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `AGENTS/PROJECT_CONTEXT.md`, `AGENTS/HANDOFF.md`, `AGENTS/STATE.md`, gitignored `AGENTS/AGENTS_LOGS/`.
  - `docs/TOOLCHAINS.md`, `docs/ARCHITECTURE.md`, `.github/workflows/ci.yml`.

## Verified Baseline (2026-11-23)
All checks executed in WSL2 Ubuntu inside `~/projects/project-asmodeus-vc` after final edits:
- `git init -b main` -> initialized (`main` branch, 0 commits; waiting for Jeremie's manual first commit).
- `uv sync` -> resolved and installed cleanly (`Python 3.12.13`, 19 packages).
- `uv run ruff format --check .` -> `22 files already formatted`.
- `uv run ruff check .` -> `All checks passed!`.
- `uv run mypy src tests` -> `Success: no issues found in 13 source files`.
- `uv run pytest -q` -> **`45 passed in 3.82s`** (covers all 5 flavors, all 4 overlays, Study/Build mode toggles, root `.dockerignore` placement, AST domain purity, CLI).
- `uv run asmodeus list` -> printed all 5 flavors and all 4 overlays.
- `uv run asmodeus doctor` -> `6/12` detected (`git`, `python3`, `uv`, `node`, `npm`, `docker`); `rustc`, `cargo`, `go`, `java`, `scala`, `sbt` reported `[MISSING]` (install instructions in `docs/TOOLCHAINS.md`).
- **End-to-end scaffold smoke test (`smoke-demo --flavor python-hex --all-overlays --study-mode`):**
  - `Files written: 43 (verified 43 files)`
  - `uv sync` -> succeeded (21 packages)
  - `uv run ruff check .` -> `All checks passed!`
  - `uv run mypy src tests` -> `Success: no issues found in 18 source files`
  - `uv run pytest -q` -> **`8 passed in 0.49s`** (cleaned up `/tmp/asmodeus-smoke` afterwards).
- **Independent Frontier Audit (`antigravity_antigravity_5`, Orchestrator Neon High) & Post-Fix Re-Verification:**
  - Inspected all 63 template files across `ts-webui`, `rust-service`, `go-service`, `scala-spark`, and all 4 overlays (`agents`, `compose`, `vm`, `github`), catching and fixing **8** issues:
    1. `templates/flavors/ts-webui/.github/workflows/ci.yml.tmpl`: fall back to `npm install` when `package-lock.json` is absent.
    2. `templates/flavors/rust-service/src/domain/mod.rs.tmpl`: wrap multi-field `Ok(Self { ... })` literal for `rustfmt` (`struct_lit_width`).
    3. `templates/flavors/rust-service/src/main.rs.tmpl`: shorten `tracing::info!` startup call within `rustfmt` `fn_call_width` while preserving shutdown guidance in comment.
    4. `templates/flavors/scala-spark/build.sbt.tmpl`: share `sparkJavaOptions` (`--add-opens`) and enable forking on both `Compile / run` and `Test`.
    5. `templates/flavors/scala-spark/Dockerfile.tmpl`: install Spark `3.5.3` (`hadoop3-scala2.13`) and launch via `spark-submit` instead of bare `java -jar`.
    6. `templates/overlays/vm/deploy/{{project_name}}.service.tmpl`: move `StartLimitIntervalSec=300` and `StartLimitBurst=5` from `[Service]` into `[Unit]`.
    7. `templates/overlays/vm/deploy/backup.sh.tmpl`: pass `.timeout 5000` via `sqlite3 -cmd ".timeout 5000"` for SQLite `< 3.41` compatibility.
    8. Moved `templates/overlays/compose/docker/.dockerignore.tmpl` to `templates/overlays/compose/.dockerignore.tmpl` (with `target/*` + `!target/scala-2.13/*.jar` exception) and added regression assertions in `tests/test_scaffold_all_flavors.py`.
  - Post-fix re-verification: `uv run ruff format --check .` (`22 files already formatted`), `uv run ruff check .` (`All checks passed!`), `uv run mypy src tests` (`Success: no issues found in 13 source files`), `uv run pytest -q` (`45 passed in 3.82s`), and `smoke-spark --flavor scala-spark --all-overlays --study-mode` (`Files written: 29`, `.dockerignore` verified at root, `OK: verified 29 files`).

## Not Yet Run (Toolchain Pending)
- Live compilation/testing of generated `ts-webui` (pending Node TLS CA check), `rust-service` (`cargo`), `go-service` (`go`), and `scala-spark` (`sbt`) outputs outside `pytest` structural checks.

## Next Steps for Jeremie / Maintainers
1. Review `git status` and make the first manual commit on `main`.
2. Install Rust, Go, and SDKMAN Java/Scala/sbt per `docs/TOOLCHAINS.md` whenever ready to compile those flavor outputs locally.
