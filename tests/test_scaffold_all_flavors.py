"""End-to-end tests across all 5 flavors, overlays, and CLI commands."""

import json
import tomllib
from pathlib import Path

import pytest

from asmodeus.cli import main
from asmodeus.domain.models import Flavor, Overlay, ProjectSpec
from asmodeus.engine.renderer import scaffold_project
from asmodeus.engine.verifier import verify_project
from asmodeus.templates_registry import repo_templates_root


def _validate_structured_manifests(target_dir: Path) -> None:
    """Validate rendered pyproject.toml and package.json files when present."""
    pyproject_path = target_dir / "pyproject.toml"
    if pyproject_path.is_file():
        parsed_toml = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
        assert isinstance(parsed_toml, dict)

    package_json_path = target_dir / "package.json"
    if package_json_path.is_file():
        parsed_json = json.loads(package_json_path.read_text(encoding="utf-8"))
        assert isinstance(parsed_json, dict)


def _create_synthetic_templates(root: Path) -> None:
    """Create minimal synthetic flavor and overlay templates for CLI roundtrip tests."""
    for flavor in Flavor:
        fdir = root / "flavors" / flavor.value
        (fdir / "src" / "{{package_name}}").mkdir(parents=True)
        (fdir / ".gitignore.tmpl").write_text(".venv/\n.env\n", encoding="utf-8")
        (fdir / "README.md.tmpl").write_text(
            "# {{project_name}}\n{{#if study_mode}}\nStudy notes.\n{{/if}}\n",
            encoding="utf-8",
        )
        (fdir / "src" / "{{package_name}}" / "main.py.tmpl").write_text(
            'APP = "{{pascal_name}}"\n',
            encoding="utf-8",
        )

    for overlay in Overlay:
        odir = root / "overlays" / overlay.value
        odir.mkdir(parents=True)
        (odir / f"OVERLAY_{overlay.value.upper()}.md.tmpl").write_text(
            "# {{project_name}} overlay\n",
            encoding="utf-8",
        )


@pytest.mark.parametrize("flavor", list(Flavor))
def test_scaffold_real_flavor_minimal(flavor: Flavor, tmp_path: Path) -> None:
    """Scaffold every real flavor in Build Mode and verify generated files."""
    templates_root = repo_templates_root()
    if not (templates_root / "flavors" / flavor.value).is_dir():
        pytest.skip(f"Template for flavor '{flavor.value}' is not present yet.")

    spec = ProjectSpec(project_name=f"demo-{flavor.value}", flavor=flavor)
    target_dir = tmp_path / spec.project_name
    result = scaffold_project(spec, target_dir)

    assert len(result.files_written) > 0
    report = verify_project(target_dir)
    assert report.ok, f"Verify failed for {flavor.value}: {report.issues}"
    assert report.issues == ()
    assert report.checked_files > 0
    _validate_structured_manifests(target_dir)


@pytest.mark.parametrize("flavor", list(Flavor))
def test_scaffold_real_flavor_all_overlays_study_mode(flavor: Flavor, tmp_path: Path) -> None:
    """Scaffold every real flavor with all overlays and Study Mode enabled."""
    templates_root = repo_templates_root()
    if not (templates_root / "flavors" / flavor.value).is_dir():
        pytest.skip(f"Template for flavor '{flavor.value}' is not present yet.")
    if not all((templates_root / "overlays" / overlay.value).is_dir() for overlay in Overlay):
        pytest.skip("Not all overlay templates are present yet.")

    spec = ProjectSpec(
        project_name=f"study-{flavor.value}",
        flavor=flavor,
        overlays=tuple(Overlay),
        study_mode=True,
    )
    target_dir = tmp_path / spec.project_name
    result = scaffold_project(spec, target_dir)

    assert len(result.files_written) > 0
    report = verify_project(target_dir)
    assert report.ok, f"Verify failed for {flavor.value} (all overlays): {report.issues}"
    assert report.issues == ()
    assert report.checked_files > 0
    _validate_structured_manifests(target_dir)
    assert (target_dir / ".dockerignore").is_file()
    assert not (target_dir / "docker" / ".dockerignore").exists()


def test_cli_list_and_doctor(capsys: pytest.CaptureFixture[str]) -> None:
    """CLI `list` and `doctor` exit 0 and print expected flavors, overlays, and docs link."""
    assert main(["list"]) == 0
    list_output = capsys.readouterr().out
    for flavor in Flavor:
        assert flavor.value in list_output
    for overlay in Overlay:
        assert overlay.value in list_output

    assert main(["doctor"]) == 0
    doctor_output = capsys.readouterr().out
    assert "docs/TOOLCHAINS.md" in doctor_output


def test_cli_new_and_verify_roundtrip(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """CLI `new` and `verify` work end-to-end with --all-overlays and --study-mode."""
    synth_root = tmp_path / "templates"
    _create_synthetic_templates(synth_root)
    monkeypatch.setattr("asmodeus.templates_registry.repo_templates_root", lambda: synth_root)

    out_dir = tmp_path / "workspace" / "sample-app"
    exit_code = main(
        [
            "new",
            "sample-app",
            "--flavor",
            "python-hex",
            "--all-overlays",
            "--study-mode",
            "--out",
            str(out_dir),
        ]
    )
    assert exit_code == 0
    assert (out_dir / "src" / "sample_app" / "main.py").is_file()
    assert "Study notes." in (out_dir / "README.md").read_text(encoding="utf-8")
    for overlay in Overlay:
        assert (out_dir / f"OVERLAY_{overlay.value.upper()}.md").is_file()

    assert main(["verify", str(out_dir)]) == 0
    assert "OK:" in capsys.readouterr().out


def test_cli_new_rejects_invalid_slug(tmp_path: Path) -> None:
    """CLI `new` returns exit code 1 when given an invalid project slug."""
    exit_code = main(
        [
            "new",
            "Invalid_Slug",
            "--flavor",
            "python-hex",
            "--out",
            str(tmp_path / "bad"),
        ]
    )
    assert exit_code == 1
