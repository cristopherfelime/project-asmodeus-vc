# `project-asmodeus-vc` — Maintainer Handoff Brief

Welcome, future maintainer (Jasmin on **Antigravity** / **Antigravity - 2** or Ezra)! Read `AGENTS/PROJECT_CONTEXT.md` and `AGENTS/STATE.md` first, then inspect the newest working log in `AGENTS/AGENTS_LOGS/`.

---

## Quick Orientation
- **What this repo is:** Polyglot hexagonal starter template generator (`asmodeus-starter`, Python 3.12 + Pydantic v2 + Hatchling + `uv`).
- **Workspace location:** `~/projects/project-asmodeus-vc`. Companion learning sandbox lives at `~/projects/project-beelzebub-vc`.
- **Who commits:** Jeremie executes all `git commit`, `git tag`, and `git push` commands manually.

---

## Template Authoring Guardrails
When adding or editing templates under `templates/`:
1. Append `.tmpl` to any file containing conditionals or `{{var}}` placeholders (including `.gitignore.tmpl`, `README.md.tmpl`, `.github/workflows/ci.yml.tmpl`).
2. Only use supported variables (`project_name`, `package_name`, `crate_name`, `pascal_name`, `go_module`, `scala_package`, `description`, `author`, `github_user`, `year`) and supported `#if` flags (`study_mode`, `with_compose`, `with_vm`, `with_agents`, `with_github`).
3. Put `#if` / `else` / `/if` directives on their own line.
4. Use `${{ ... }}` for GitHub Actions expressions and `$VAR` / `${VAR}` (never `{{...}}`) in Docker/shell commands so `verify_project` never flags false positives.

---

## When You Finish a Working Session
1. Run `uv run ruff format --check .`, `uv run ruff check .`, `uv run mypy src tests`, and `uv run pytest -q`.
2. Update `AGENTS/STATE.md` with exact observed outputs.
3. Add an immutable working log in `AGENTS/AGENTS_LOGS/LOG_YYYYMMDD_HHMMSS_<AGENT>.md` (gitignored).
4. Leave diffs clean for Jeremie to inspect and commit.
