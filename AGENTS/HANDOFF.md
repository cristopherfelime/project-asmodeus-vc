# `project-asmodeus-vc` — Full Maintainer & Cold-Start Handoff Guide

Welcome, future Jasmin (Gemini) or Ezra (Claude)! This document is the self-contained handoff brief for continuing development of **Asmodeus** (`asmodeus-starter`) directly inside its own dedicated repository (`\\wsl.localhost\Ubuntu\home\user\projects\project-asmodeus-vc`).

Always read `AGENTS/PROJECT_CONTEXT.md` and `AGENTS/STATE.md` first, check `git status` / recent commits (`2a73fa3`), and write a NEW immutable session log under `AGENTS/AGENTS_LOGS/` whenever completing a milestone.

---

## 1. Where Things Stand Right Now

- **Git Status at Handoff:** Clean base commit **`2a73fa3`** (`chore(Asmodeus): initial polyglot hexagonal scaffolder`) on `main`, plus updated `AGENTS/{PROJECT_CONTEXT,STATE,HANDOFF}.md` waiting for Jeremie's manual commit.
- **Core Package (`src/asmodeus/`):**
  - `domain/models.py`: Pure Pydantic v2 frozen `Flavor` (`python-hex`, `ts-webui`, `rust-service`, `go-service`, `scala-spark`), `Overlay` (`agents`, `compose`, `vm`, `github`), `ProjectSpec` validation + derived token naming, `RenderResult`, `VerifyIssue`, `VerifyReport`. AST boundary enforced by `tests/test_code_boundaries.py`.
  - `templates_registry.py`: Discovers flavors and overlays cleanly under `templates/`.
  - `engine/renderer.py`: Renders nested `{{#if <flag>}}`/`{{else}}`/`{{/if}}` conditionals (`study_mode`, `with_compose`, `with_vm`, `with_agents`, `with_github`), substitutes `{{var}}` in paths & contents while preserving GitHub Actions `${{ ... }}` via negative lookbehind, strips `.tmpl`, marks `.sh` executable (`0o755`), and rejects non-empty destinations unless `--force`.
  - `engine/verifier.py`: Validates generated `.gitignore`, `README.md`, absence of `.env*` secrets, and zero leftover unrendered `{{...}}` placeholders.
  - `cli.py`: `asmodeus list`, `asmodeus new`, `asmodeus verify`, `asmodeus doctor`.
- **Verified Baseline (from initial release + post-audit fix pass `2a73fa3`, docs-only changes since):**
  - `uv run ruff format --check .` -> `22 files already formatted`
  - `uv run ruff check .` -> `All checks passed!`
  - `uv run mypy src tests` -> `Success: no issues found in 13 source files`
  - `uv run pytest -q` -> **`45 passed in 3.82s`**
  - End-to-end smoke checks: `smoke-demo` (`python-hex`, 43 files, `8 passed in 0.49s` pytest) & `smoke-spark` (`scala-spark`, 29 files, root `.dockerignore` verified).
  - Independent frontier audit (`antigravity_antigravity_5`, high thought) reviewed all 63 template files and fixed 8 edge cases (`ts-webui` CI fallback, `rust-service` formatting, `scala-spark` JVM/Docker `spark-submit`, `vm` systemd `[Unit]` limits + `backup.sh` timeout flag, and root `.dockerignore.tmpl`).
- **Companion Project:** `~/projects/project-beelzebub-vc` (**Beelzebub v2**, complete 8-Unit / 42-Chapter Engineering Academy & Capstone Studio) links its Capstone workspace initialization guidance to `asmodeus new`.

---

## 2. Antigravity Account Routing Policy & Current Quota Snapshot

**CRITICAL ACCOUNT RULES (set by Jeremie for the new Asmodeus project):**
1. **NEVER use Account #1 (`Antigravity`) or Account #2 (`Antigravity - 2`)** — those are Jeremie's primary and secondary personal accounts.
2. **Main planner / primary conversation thread:** Run on **Account #7 (`antigravity_antigravity_7`)** (`100%` 5-hour / `95%` weekly / `100%` Argon).
3. **Subagents / Delegates:** Route **exclusively to Accounts #3–6 (`antigravity_antigravity_3` through `antigravity_antigravity_6`)**, preferring **#5 and #6** (`100%` 5h / `92–94%` weekly) first, then **#4** (`87%` 5h / `89%` weekly), while keeping **#3** (`50%` 5h / `59%` weekly) light until its 5h window resets.

### Usage Snapshot at Handoff (2026-11-23 22:55 +08:00)

| Account | Gemini 5-hour | Gemini Weekly | Gemini 4 Argon Weekly | Claude & GPT 5-hour | Claude & GPT Weekly | Assigned Role |
| --- | --- | --- | --- | --- | --- | --- |
| **#1 (`Antigravity`)** | `100%` | `89%` | `0%` | `100%` | `37%` | **DO NOT USE (Primary)** |
| **#2 (`Antigravity - 2`)** | `100%` | `82%` | `41%` | `100%` | `100%` | **DO NOT USE (Secondary)** |
| **#3 (`Antigravity - 3`)** | `50%` | `59%` | `96%` | `100%` | `100%` | **Delegate Pool (Low 5h — use lightly)** |
| **#4 (`Antigravity - 4`)** | `87%` | `89%` | `100%` | `100%` | `100%` | **Delegate Pool** |
| **#5 (`Antigravity - 5`)** | `100%` | `92%` | `100%` | `100%` | `100%` | **Delegate Pool (Fresh — Priority 1)** |
| **#6 (`Antigravity - 6`)** | `100%` | `94%` | `100%` | `100%` | `100%` | **Delegate Pool (Fresh — Priority 1)** |
| **#7 (`Antigravity - 7`)** | `100%` | `95%` | `100%` | `100%` | `100%` | **Main Planner / Coordinator** |
| **Pool Totals (screenshot)** | `91% avg` | `86% avg` | `77% avg` | `100% avg` | `91% avg` | - |

*(Jeremie will also drop an updated screenshot in the new Asmodeus project thread if quotas shift.)*

---

## 3. Template Authoring & Engineering Guardrails

1. **Domain Purity:** `src/asmodeus/domain/` must stay free of OS/I/O/network imports (`tests/test_code_boundaries.py` enforces via AST).
2. **Template Rules:**
   - Append `.tmpl` to any file under `templates/` containing conditionals or `{{var}}` tokens.
   - Allowed variables: `project_name`, `package_name`, `crate_name`, `pascal_name`, `go_module`, `scala_package`, `description`, `author`, `github_user`, `year`.
   - Allowed `#if` flags: `study_mode`, `with_compose`, `with_vm`, `with_agents`, `with_github` (directives on their own lines).
   - Keep GitHub Actions expressions `${{ ... }}` intact and use `$VAR` / `${VAR}` (never `{{...}}`) in Dockerfiles and shell scripts.
3. **Manual Git Policy:** NEVER run `git commit`, `git tag`, or `git push` autonomously — Jeremie commits manually.
4. **Immutable Logs & Persona:** Write NEW session logs to gitignored `AGENTS/AGENTS_LOGS/LOG_*.md`; keep Jasmin's responses clear, cheerful, and using **kaomojis ONLY — ZERO emojis**.
5. **PowerShell -> WSL Quoting:** Never put `"`, unquoted `()`, or `|` inside `wsl -e bash -lc '...'`.

---

## 4. Recommended Next Milestones in the Dedicated Asmodeus Workspace

1. **Update `templates/overlays/agents/AGENTS/HANDOFF.md.tmpl`:** Sync the generated project template's `AGENTS/` overlay so newly scaffolded repos reflect any updated team/account/workflow conventions cleanly.
2. **Live Compile/Build Verification Across All 5 Flavors:**
   - Node/npm is available in WSL2 now (`node v24+`), so run `npm install && npm run typecheck && npm run build` inside a smoke-generated `ts-webui` project!
   - Install `rustc`/`cargo`, `go`, and `java`/`scala`/`sbt` per `docs/TOOLCHAINS.md`, verify `uv run asmodeus doctor` shows `12/12`, and compile-test generated `rust-service`, `go-service`, and `scala-spark` outputs end-to-end.
3. **Optional New Flavors / Overlays Aligned with Beelzebub v2 Capstones:**
   - Consider adding a `data-duckdb-polars` flavor (or `--with-k8s` / `--with-gcp-cloudrun` overlay + optional Git hygiene audit integration matching Beelzebub's `capstones/tools/git_audit.py` standards) for Data Engineering / MLOps / GKE Capstones.

---

## 5. Copy-Pasteable Cold-Start Handoff Prompt

Paste this exact prompt into the first message of the new T3 Code thread rooted in `\\wsl.localhost\Ubuntu\home\user\projects\project-asmodeus-vc`:

```text
Hey Jasmin! We're continuing `project-asmodeus-vc` (`asmodeus-starter`) here in its own dedicated workspace.

Before doing anything else:
1. Read `AGENTS/PROJECT_CONTEXT.md`, `AGENTS/STATE.md`, `AGENTS/HANDOFF.md`, `docs/ARCHITECTURE.md`, and the latest logs in `AGENTS/AGENTS_LOGS/`.
2. Keep every non-negotiable invariant intact:
   - `src/asmodeus/domain/` stays pure Python/Pydantic (zero OS/I/O/network imports; enforced by `tests/test_code_boundaries.py`).
   - `.tmpl` suffix on any template with `{{var}}` or `{{#if ...}}`; preserve GitHub Actions `${{ ... }}` expressions.
   - Never run `git commit` or `git push` (I commit manually).
   - Keep `AGENTS/AGENTS_LOGS/` immutable (write new log files instead of overwriting old ones).
   - Respond as Jasmin with kaomojis ONLY — zero emojis.
3. Antigravity Account & Usage Limit Rules (I will attach the latest usage screenshot too):
   - NEVER use Account #1 (`Antigravity`) or Account #2 (`Antigravity - 2`) — they are my primary and secondary personal accounts.
   - Keep this main planner/coordinator session on **Account #7 (`antigravity_antigravity_7`)** (`100%` 5h / `95%` weekly / `100%` Argon).
   - Delegate subagent/frontier work exclusively to **Accounts #3–6 (`antigravity_antigravity_3`..`6`)**, prioritizing **#5 and #6** (`100%` 5h / `92–94%` weekly) first, then **#4** (`87%` 5h / `89%` weekly), while keeping **#3** (`50%` 5h / `59%` weekly) light until its 5h window resets.
   - Baseline usage at handoff (2026-11-23 22:55 +08:00):
     * Gemini 5-hour (91% avg): #1 100%, #2 100%, #3 50%, #4 87%, #5 100%, #6 100%, #7 100%
     * Gemini Weekly (86% avg): #1 89%, #2 82%, #3 59%, #4 89%, #5 92%, #6 94%, #7 95%
     * Gemini 4 Argon Weekly (77% avg): #1 0%, #2 41%, #3 96%, #4-7 100%
     * Claude & GPT 5-hour: 100% across all #1-#7
     * Claude & GPT Weekly (91% avg): #1 37%, #2-7 100%
4. When running commands from Windows into WSL2 Ubuntu (`~/projects/project-asmodeus-vc`), avoid `"`, `|`, and unquoted `()` inside `wsl -e bash -lc '...'`.
5. Current verified baseline at handoff (`2a73fa3` + docs update):
   - `uv run ruff format --check .` -> 22 files formatted
   - `uv run ruff check .` -> All checks passed
   - `uv run mypy src tests` -> 0 errors across 13 source files
   - `uv run pytest -q` -> 45 passed
   - `asmodeus doctor` previously saw 6/12 tools (`git`, `python3`, `uv`, `node`, `npm`, `docker`); `rustc`/`cargo`, `go`, and `java`/`scala`/`sbt` still need setup per `docs/TOOLCHAINS.md`.

Once you've oriented yourself (no need to re-run tests unless we inspect/edit code/templates), confirm what you loaded and ask which Asmodeus milestone we want to tackle next (for example: live-compiling `ts-webui` + remaining polyglot flavors via `docs/TOOLCHAINS.md`, updating `templates/overlays/agents/`, or adding Beelzebub v2-aligned templates/overlays like DuckDB/Polars or K8s/Cloud Run)!
```
