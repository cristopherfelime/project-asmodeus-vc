# project-asmodeus-vc (`asmodeus-starter`)

A polyglot hexagonal project scaffolder for WSL2 Ubuntu and Linux workflows, featuring composable overlays and a first-class **Study Mode vs Build Mode** toggle.

---

## Key Features

- **Five Production Flavors:** Scaffold clean hexagonal starter repositories in Python, TypeScript, Rust, Go, or Scala/Spark.
- **Composable Overlays:** Layer agent constitutions, Docker Compose environments, VM setup helpers, and GitHub Actions workflows cleanly on top of any flavor.
- **Study Mode vs Build Mode:**
  - **Build Mode (default):** Lean, production-oriented starter output with minimal boilerplate.
  - **Study Mode (`--study-mode`):** Enables conditional `{{#if study_mode}}` learning blocks across templates—adding architectural callouts, boundary explanations, and guided study checkpoints without altering runtime semantics.
- **Built-in Verification:** Every `asmodeus new` run automatically validates the generated directory via `verify_project` (ensuring `.gitignore`, `README.md`, no leaked `.env` secrets, and zero unrendered `{{...}}` placeholders while preserving GitHub Actions `${{ ... }}` expressions).
- **Toolchain Doctor:** Inspect local WSL2 / Linux toolchains (`uv`, `node`, `rustc`, `cargo`, `go`, `java`, `scala`, `sbt`, `docker`) with `asmodeus doctor`.

---

## Flavors

| Flavor ID | Stack & Architecture |
|---|---|
| `python-hex` | Python 3.12 hexagonal starter (`uv`, `pydantic`, `pytest`, `ruff`, `mypy`) |
| `ts-webui` | TypeScript Web UI / frontend starter (`node`, `npm`) |
| `rust-service` | Rust service starter with domain/port separation (`cargo`, `rustc`) |
| `go-service` | Go service starter with clean package boundaries (`go`) |
| `scala-spark` | Scala / Apache Spark starter (`java`, `scala`, `sbt`) |

---

## Composable Overlays

| Overlay ID | CLI Flag | Purpose |
|---|---|---|
| `agents` | `--with-agents` | Symmetrical Jasmin & Ezra `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` / `AGENTS/STATE.md` setup |
| `compose` | `--with-compose` | Container Compose definition and sanitized `.env.compose.example` |
| `vm` | `--with-vm` | VM provisioning and local environment scripts |
| `github` | `--with-github` | GitHub Actions CI workflow (preserving `${{ ... }}` expressions) |

Pass `--all-overlays` to apply all four overlays in deterministic order (`agents`, `compose`, `vm`, `github`).

---

## Quickstart

Ensure Python 3.12+ and `uv` are installed (see [docs/TOOLCHAINS.md](docs/TOOLCHAINS.md)).

```bash
# Install project and dev dependencies
uv sync

# List available flavors and overlays
uv run asmodeus list

# Check installed WSL2 / Linux toolchains
uv run asmodeus doctor
```

---

## CLI Usage

### Scaffold a new project

```bash
# Minimal Build Mode scaffold into ./billing-core
uv run asmodeus new billing-core --flavor python-hex

# Specify an explicit target directory with --out
uv run asmodeus new billing-core --flavor rust-service --out /tmp/billing-core

# Enable overlays and Study Mode
uv run asmodeus new lakehouse-job \
  --flavor scala-spark \
  --with-agents \
  --with-github \
  --study-mode

# Apply every overlay and overwrite an existing directory
uv run asmodeus new portal-ui \
  --flavor ts-webui \
  --all-overlays \
  --out ./out/portal-ui \
  --author "Jeremie" \
  --github-user "cristopherfelime" \
  --description "Internal analytics web console" \
  --force
```

> **Note on `--out`:** `--out <dir>` sets the exact destination directory for the scaffolded project. When omitted, `asmodeus new` writes into `./<project_name>`.

### Verify an existing project

```bash
uv run asmodeus verify ./billing-core
```

---

## Quality Gates

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest -q
```

---

## Further Reading

- [Toolchain Setup Guide (WSL2 Ubuntu)](docs/TOOLCHAINS.md) — installing `uv`, Node.js/npm, Rust, Go, Java/Scala/sbt, and Docker.
- [Architecture & Boundary Guide](docs/ARCHITECTURE.md) — hexagonal layer separation, 4-Hop boundary trace hygiene, template directives, and Study Mode vs Build Mode.
- [Agent Constitution](AGENTS.md) — shared workflow rules for Jasmin & Ezra.
