"""Tests for template conditional evaluation, variable substitution, and verification."""

from pathlib import Path

import pytest

from asmodeus.domain.models import Flavor, Overlay, ProjectSpec
from asmodeus.engine.renderer import (
    TemplateSyntaxError,
    render_conditionals,
    render_template_text,
    scaffold_project,
    substitute_variables,
)
from asmodeus.engine.verifier import verify_project


def test_render_conditionals_if_else_and_nested() -> None:
    """Conditionals support if/else and nested blocks without leaking inactive branches."""
    template = (
        "header\n"
        "{{#if study_mode}}\n"
        "study-on\n"
        "{{#if with_compose}}\n"
        "nested-compose-on\n"
        "{{else}}\n"
        "nested-compose-off\n"
        "{{/if}}\n"
        "{{else}}\n"
        "build-on\n"
        "{{/if}}\n"
        "footer\n"
    )

    study_with_compose = render_conditionals(
        template,
        {"study_mode": True, "with_compose": True},
    )
    assert study_with_compose == "header\nstudy-on\nnested-compose-on\nfooter\n"

    study_no_compose = render_conditionals(
        template,
        {"study_mode": True, "with_compose": False},
    )
    assert study_no_compose == "header\nstudy-on\nnested-compose-off\nfooter\n"

    build_with_compose = render_conditionals(
        template,
        {"study_mode": False, "with_compose": True},
    )
    assert build_with_compose == "header\nbuild-on\nfooter\n"


@pytest.mark.parametrize(
    "bad_template",
    [
        "{{#if unknown_flag}}\nx\n{{/if}}\n",
        "{{#if study_mode}}\n{{#if bad_nested}}\n{{/if}}\n{{/if}}\n",
        "{{#if study_mode}}\nunclosed\n",
        "{{else}}\nstray-else\n",
        "{{#if study_mode}}\na\n{{else}}\nb\n{{else}}\nc\n{{/if}}\n",
        "{{/if}}\n",
        "{{#if}}\nx\n{{/if}}\n",
    ],
)
def test_render_conditionals_syntax_errors(bad_template: str) -> None:
    """Malformed directives, unknown flags, and unbalanced blocks fail loudly."""
    with pytest.raises(TemplateSyntaxError):
        render_conditionals(bad_template, {"study_mode": True})


def test_substitute_variables_preserves_github_expressions_and_rejects_typos() -> None:
    """GitHub Actions ${{ ... }} expressions survive while unknown {{...}} fail."""
    rendered = substitute_variables(
        "ref=${{ github.ref }} name={{project_name}} tok=${{ secrets.TOKEN }}\n",
        {"project_name": "demo-app"},
    )
    assert rendered == "ref=${{ github.ref }} name=demo-app tok=${{ secrets.TOKEN }}\n"

    with pytest.raises(TemplateSyntaxError):
        substitute_variables("hello {{typo}}\n", {"project_name": "demo-app"})


def test_render_template_text_drops_inactive_branch_placeholders() -> None:
    """Placeholders inside inactive conditional branches are discarded before substitution."""
    template = "{{#if study_mode}}\nignored={{unknown_key}}\n{{/if}}\nactive={{project_name}}\n"
    rendered = render_template_text(
        template,
        context={"project_name": "demo-app"},
        flags={"study_mode": False},
    )
    assert rendered == "active=demo-app\n"


def test_scaffold_project_substitutes_paths_strips_tmpl_and_layers_overlays(
    tmp_path: Path,
) -> None:
    """Scaffolder substitutes path vars, strips .tmpl, copies non-templates, and overlays."""
    templates_root = tmp_path / "templates"
    flavor_root = templates_root / "flavors" / "python-hex"
    overlay_github = templates_root / "overlays" / "github"
    overlay_compose = templates_root / "overlays" / "compose"

    (flavor_root / "src" / "{{package_name}}").mkdir(parents=True)
    (flavor_root / "assets").mkdir(parents=True)
    (flavor_root / "scripts").mkdir(parents=True)
    (overlay_github / ".github" / "workflows").mkdir(parents=True)
    overlay_compose.mkdir(parents=True)

    (flavor_root / ".gitignore.tmpl").write_text(".venv/\n.env\n", encoding="utf-8")
    (flavor_root / "README.md.tmpl").write_text("# {{pascal_name}}\n", encoding="utf-8")
    (flavor_root / "src" / "{{package_name}}" / "app.py.tmpl").write_text(
        'NAME = "{{project_name}}"\n',
        encoding="utf-8",
    )
    (flavor_root / "assets" / ".gitkeep").write_bytes(b"\x00keep")
    (flavor_root / "scripts" / "check.sh.tmpl").write_text(
        "#!/usr/bin/env sh\necho {{project_name}}\n",
        encoding="utf-8",
    )
    (overlay_github / ".github" / "workflows" / "ci.yml.tmpl").write_text(
        "name: {{project_name}}\nref: ${{ github.ref }}\ntok: ${{ secrets.API_KEY }}\n",
        encoding="utf-8",
    )
    (overlay_compose / ".env.compose.example.tmpl").write_text(
        "APP_NAME={{project_name}}\n",
        encoding="utf-8",
    )

    spec = ProjectSpec(
        project_name="demo-app",
        flavor=Flavor.PYTHON_HEX,
        overlays=(Overlay.COMPOSE, Overlay.GITHUB),
    )
    target_dir = tmp_path / "out"
    result = scaffold_project(spec, target_dir, templates_root=templates_root)

    app_py = (target_dir / "src" / "demo_app" / "app.py").read_text(encoding="utf-8")
    ci_yml = (target_dir / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert (target_dir / ".gitignore").is_file()
    assert (target_dir / "README.md").read_text(encoding="utf-8") == "# DemoApp\n"
    assert app_py == 'NAME = "demo-app"\n'
    assert (target_dir / "assets" / ".gitkeep").read_bytes() == b"\x00keep"
    assert (target_dir / "scripts" / "check.sh").is_file()
    assert "${{ github.ref }}" in ci_yml
    assert "${{ secrets.API_KEY }}" in ci_yml
    assert (target_dir / ".env.compose.example").is_file()
    assert "src/demo_app/app.py" in result.files_written

    report = verify_project(target_dir)
    assert report.ok is True
    assert report.issues == ()


def test_scaffold_project_rejects_non_empty_dir_unless_forced(tmp_path: Path) -> None:
    """Non-empty target directories fail unless force=True is specified."""
    templates_root = tmp_path / "templates"
    flavor_root = templates_root / "flavors" / "go-service"
    flavor_root.mkdir(parents=True)
    (flavor_root / ".gitignore.tmpl").write_text(".env\n", encoding="utf-8")
    (flavor_root / "README.md.tmpl").write_text("# {{project_name}}\n", encoding="utf-8")

    target_dir = tmp_path / "existing"
    target_dir.mkdir()
    (target_dir / "sentinel.txt").write_text("keep", encoding="utf-8")

    spec = ProjectSpec(project_name="go-demo", flavor=Flavor.GO_SERVICE)
    with pytest.raises(FileExistsError):
        scaffold_project(spec, target_dir, templates_root=templates_root)

    result = scaffold_project(spec, target_dir, templates_root=templates_root, force=True)
    assert "README.md" in result.files_written
    assert (target_dir / "sentinel.txt").is_file()


def test_verify_project_flags_missing_files_secrets_and_placeholders(tmp_path: Path) -> None:
    """verify_project catches missing files, .env files, and unrendered {{...}}."""
    missing_report = verify_project(tmp_path / "does-not-exist")
    assert missing_report.ok is False
    assert missing_report.issues[0].code == "missing-target"

    project_dir = tmp_path / "broken"
    project_dir.mkdir()
    empty_report = verify_project(project_dir)
    assert empty_report.ok is False
    assert {issue.code for issue in empty_report.issues} == {
        "missing-gitignore",
        "missing-readme",
    }

    (project_dir / ".gitignore").write_text(".env\n", encoding="utf-8")
    (project_dir / "README.md").write_text("ok\n", encoding="utf-8")
    (project_dir / ".env.example").write_text("KEY=example\n", encoding="utf-8")
    (project_dir / ".env").write_text("SECRET=123\n", encoding="utf-8")
    (project_dir / ".env.local").write_text("SECRET=456\n", encoding="utf-8")
    (project_dir / "notes.txt").write_text(
        "ok=${{ github.sha }}\nbad={{unrendered_token}}\n",
        encoding="utf-8",
    )

    report = verify_project(project_dir)
    assert report.ok is False
    issue_pairs = {(issue.path, issue.code) for issue in report.issues}
    assert (".env", "forbidden-env-file") in issue_pairs
    assert (".env.local", "forbidden-env-file") in issue_pairs
    assert ("notes.txt", "unrendered-placeholder") in issue_pairs
    assert (".env.example", "forbidden-env-file") not in issue_pairs
    assert len(report.issues) == 3
