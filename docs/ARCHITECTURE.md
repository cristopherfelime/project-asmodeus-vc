# Asmodeus Architecture Guide

`project-asmodeus-vc` (`asmodeus-starter`) is structured around **Hexagonal Architecture (Ports & Adapters)** and **4-Hop Boundary Trace Hygiene**.

---

## 1. Hexagonal Boundaries

```text
+-------------------------------------------------------------------+
|  CLI Adapter: src/asmodeus/cli.py                                 |
|  - Argument parsing, overlay flags, stdout/stderr formatting      |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|  Pure Domain Core: src/asmodeus/domain/models.py                  |
|  - Flavor, Overlay, ProjectSpec (slug & identifier derivation)    |
|  - RenderResult, VerifyIssue, VerifyReport                        |
|  - ZERO filesystem, subprocess, network, or wall-clock I/O        |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|  Engine & Template Registry                                       |
|  - src/asmodeus/templates_registry.py (flavor/overlay path lookup)|
|  - src/asmodeus/engine/renderer.py (conditionals & placeholders)  |
|  - src/asmodeus/engine/verifier.py (post-render invariant audit)  |
+-------------------------------------------------------------------+
```

### Enforced Domain Purity

Every file under `src/asmodeus/domain/` is forbidden from importing I/O or system modules (`os`, `pathlib`, `sys`, `subprocess`, `shutil`, `json`, `urllib`, `httpx`, `sqlite3`) or calling `datetime.now()`.

This invariant is continuously verified by AST inspection in `tests/test_code_boundaries.py`.

---

## 2. 4-Hop Boundary Trace Hygiene

A clean trace through Asmodeus touches at most four clear architectural hops:

1. **Hop 1 — Entry / CLI (`asmodeus.cli`):** Parses CLI flags (`new`, `verify`, `list`, `doctor`), converts flags into domain inputs, and handles process exit codes (`0` or `1`).
2. **Hop 2 — Pure Domain (`asmodeus.domain.models`):** Validates `ProjectSpec` (`project_name` kebab-case slug, deduplicated `overlays`, derived `package_name`, `crate_name`, `pascal_name`, `go_module`, `scala_package`) and yields immutable `template_context()` and `condition_flags()`.
3. **Hop 3 — Application Engine (`asmodeus.engine` + `asmodeus.templates_registry`):** Resolves the base flavor directory and selected overlay directories, evaluates `{{#if}}`/`{{else}}`/`{{/if}}` blocks, renders `{{var}}` substitutions in both paths and file contents, and verifies rendered files.
4. **Hop 4 — Host Boundary (Filesystem / Terminal):** Reads template bytes, writes generated files cleanly (preserving `.sh` executable permissions), and reports structured verification issues.

Keeping each module inside its hop avoids circular dependencies and lets domain rules and template rendering be exhaustively unit- and property-tested without touching real toolchains.

---

## 3. Template Contract & Composable Overlays

Templates live under `templates/`:

- `templates/flavors/<flavor>/` — Base project skeleton for `python-hex`, `ts-webui`, `rust-service`, `go-service`, or `scala-spark`.
- `templates/overlays/<overlay>/` — Optional additive layers (`agents`, `compose`, `vm`, `github`) rendered on top of the selected flavor in deterministic order.

### Rendering Rules

1. **Conditionals (line-oriented):**
   - `{{#if <flag>}}`, optional `{{else}}`, and `{{/if}}` on their own lines.
   - Supported flags: `study_mode`, `with_agents`, `with_compose`, `with_vm`, `with_github`.
   - Arbitrary nesting is supported via an explicit frame stack; unknown flags, duplicate `{{else}}`, stray `{{/if}}`, or unclosed blocks raise `TemplateSyntaxError`.
2. **Variable Substitution (paths & contents):**
   - Supported keys: `{{project_name}}`, `{{package_name}}`, `{{crate_name}}`, `{{pascal_name}}`, `{{go_module}}`, `{{scala_package}}`, `{{description}}`, `{{author}}`, `{{github_user}}`, `{{year}}`.
   - Placeholder pattern: `(?<!\$)\{\{([^{}]+)\}\}` so GitHub Actions expressions such as `${{ github.ref }}` or `${{ secrets.TOKEN }}` pass through completely untouched.
   - Unknown placeholders raise `TemplateSyntaxError` during rendering and are flagged by `verify_project`.
3. **File Handling:**
   - Files ending in `.tmpl` are rendered as UTF-8 text and written with the `.tmpl` suffix stripped.
   - Non-`.tmpl` files (such as `.gitkeep` or static binary assets) are copied verbatim.
   - Generated `.sh` scripts receive executable permissions (`0o755`).

---

## 4. Study Mode vs Build Mode

| Aspect | Build Mode (`study_mode=False`, default) | Study Mode (`--study-mode`) |
|---|---|---|
| Primary Goal | Lean, distraction-free starter codebase | Guided learning of hexagonal boundaries |
| Template Behavior | `{{#if study_mode}}` sections omitted | `{{#if study_mode}}` annotations & exercises included |
| `{{else}}` Support | Uses concise `{{else}}` branch when defined | Uses rich explanatory branch |
| Runtime Semantics | Identical domain/service behavior | Identical domain/service behavior |
