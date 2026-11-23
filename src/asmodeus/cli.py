"""Command-line interface for Asmodeus."""

import argparse
import os
import shutil
import sys
from collections.abc import Sequence
from pathlib import Path

from pydantic import ValidationError

from asmodeus.domain.models import Flavor, Overlay, ProjectSpec
from asmodeus.engine.renderer import TemplateSyntaxError, scaffold_project
from asmodeus.engine.verifier import verify_project
from asmodeus.templates_registry import list_flavors, list_overlays

TOOLCHAINS: tuple[str, ...] = (
    "git",
    "python3",
    "uv",
    "node",
    "npm",
    "rustc",
    "cargo",
    "go",
    "java",
    "scala",
    "sbt",
    "docker",
)

__all__ = [
    "TOOLCHAINS",
    "build_parser",
    "main",
]


def build_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the `asmodeus` CLI."""
    parser = argparse.ArgumentParser(
        prog="asmodeus",
        description="Scaffold and verify polyglot hexagonal projects.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List available flavors and overlays.")

    new_parser = subparsers.add_parser("new", help="Scaffold a new project.")
    new_parser.add_argument("project_name", help="Kebab-case project name slug.")
    new_parser.add_argument(
        "--flavor",
        required=True,
        choices=[flavor.value for flavor in Flavor],
        help="Base project flavor to scaffold.",
    )
    new_parser.add_argument(
        "--with-compose",
        action="store_true",
        help="Include the Docker Compose overlay.",
    )
    new_parser.add_argument(
        "--with-vm",
        action="store_true",
        help="Include the VM setup overlay.",
    )
    new_parser.add_argument(
        "--with-agents",
        action="store_true",
        help="Include the AGENTS.md / CLAUDE.md / GEMINI.md overlay.",
    )
    new_parser.add_argument(
        "--with-github",
        action="store_true",
        help="Include the GitHub Actions CI overlay.",
    )
    new_parser.add_argument(
        "--all-overlays",
        action="store_true",
        help="Enable all available overlays.",
    )
    new_parser.add_argument(
        "--study-mode",
        action="store_true",
        help="Render annotated Study Mode guidance instead of lean Build Mode.",
    )
    new_parser.add_argument(
        "--out",
        default=None,
        help="Exact target directory (default: ./<project_name>).",
    )
    new_parser.add_argument(
        "--author",
        default="Jeremie",
        help="Project author name.",
    )
    new_parser.add_argument(
        "--github-user",
        default="cristopherfelime",
        help="GitHub username for repository/module coordinates.",
    )
    new_parser.add_argument(
        "--description",
        default="A production-ready service scaffolded with Asmodeus.",
        help="Short project description.",
    )
    new_parser.add_argument(
        "--force",
        action="store_true",
        help="Allow scaffolding into an existing non-empty directory.",
    )

    verify_parser = subparsers.add_parser(
        "verify",
        help="Verify hygiene and placeholder rendering in a project directory.",
    )
    verify_parser.add_argument("target_dir", help="Project directory to inspect.")

    subparsers.add_parser(
        "doctor",
        help="Check local WSL2/Linux toolchains and print setup instructions.",
    )

    return parser


def _resolve_overlays(args: argparse.Namespace) -> tuple[Overlay, ...]:
    """Assemble overlays in deterministic order from parsed CLI flags."""
    if args.all_overlays:
        return (Overlay.AGENTS, Overlay.COMPOSE, Overlay.VM, Overlay.GITHUB)

    selected: list[Overlay] = []
    if args.with_agents:
        selected.append(Overlay.AGENTS)
    if args.with_compose:
        selected.append(Overlay.COMPOSE)
    if args.with_vm:
        selected.append(Overlay.VM)
    if args.with_github:
        selected.append(Overlay.GITHUB)
    return tuple(selected)


def _extra_tool_search_path() -> str:
    """Build a search PATH including common WSL2/Linux user toolchain directories."""
    home = Path.home()
    candidates = [
        home / ".local" / "bin",
        home / ".cargo" / "bin",
        Path("/usr/local/go/bin"),
        home / ".sdkman" / "candidates" / "java" / "current" / "bin",
        home / ".sdkman" / "candidates" / "scala" / "current" / "bin",
        home / ".sdkman" / "candidates" / "sbt" / "current" / "bin",
    ]
    existing = os.environ.get("PATH", "")
    parts = [part for part in existing.split(os.pathsep) if part]
    for candidate in candidates:
        candidate_str = str(candidate)
        if candidate_str not in parts:
            parts.append(candidate_str)
    return os.pathsep.join(parts)


def _cmd_list() -> int:
    """Print available flavors and overlays."""
    flavors = list_flavors()
    overlays = list_overlays()
    print("Available flavors:")
    for flavor in flavors:
        print(f"  - {flavor}")
    print("Available overlays:")
    for overlay in overlays:
        print(f"  - {overlay}")
    return 0


def _cmd_new(args: argparse.Namespace) -> int:
    """Scaffold a new project and verify the rendered output."""
    overlays = _resolve_overlays(args)
    try:
        spec = ProjectSpec(
            project_name=str(args.project_name),
            flavor=Flavor(str(args.flavor)),
            overlays=overlays,
            study_mode=bool(args.study_mode),
            description=str(args.description),
            author=str(args.author),
            github_user=str(args.github_user),
        )
    except ValidationError as exc:
        print(f"Invalid project specification: {exc}", file=sys.stderr)
        return 1

    out_arg: str | None = args.out
    target_dir = Path(out_arg) if out_arg is not None else Path.cwd() / spec.project_name

    try:
        result = scaffold_project(spec, target_dir, force=bool(args.force))
    except (TemplateSyntaxError, FileExistsError, FileNotFoundError, OSError) as exc:
        print(f"Scaffold failed: {exc}", file=sys.stderr)
        return 1

    report = verify_project(target_dir)
    if not report.ok:
        print(f"Verification failed for {target_dir}:", file=sys.stderr)
        for issue in report.issues:
            print(f"  - [{issue.code}] {issue.path}: {issue.message}", file=sys.stderr)
        return 1

    mode_label = "study" if spec.study_mode else "build"
    overlays_label = ", ".join(overlay.value for overlay in spec.overlays) or "none"
    print(f"Scaffolded '{spec.project_name}' ({spec.flavor.value}, {mode_label} mode)")
    print(f"Target: {target_dir}")
    print(f"Overlays: {overlays_label}")
    print(f"Files written: {len(result.files_written)} (verified {report.checked_files} files)")
    return 0


def _cmd_verify(args: argparse.Namespace) -> int:
    """Run project hygiene verification against a target directory."""
    target_dir = Path(str(args.target_dir))
    report = verify_project(target_dir)
    if report.ok:
        print(f"OK: verified {report.checked_files} files in {target_dir} with 0 issues.")
        return 0

    print(f"FAILED: found {len(report.issues)} issue(s) in {target_dir}:", file=sys.stderr)
    for issue in report.issues:
        print(f"  - [{issue.code}] {issue.path}: {issue.message}", file=sys.stderr)
    return 1


def _cmd_doctor() -> int:
    """Inspect local toolchain availability without failing on missing optional tools."""
    search_path = _extra_tool_search_path()
    found_count = 0
    print("Asmodeus toolchain check:")
    for tool in TOOLCHAINS:
        location = shutil.which(tool, path=search_path)
        if location is not None:
            found_count += 1
            print(f"  [OK]      {tool:<10} {location}")
        else:
            print(f"  [MISSING] {tool:<10} (see docs/TOOLCHAINS.md)")
    print(
        f"Summary: {found_count}/{len(TOOLCHAINS)} toolchains detected. "
        "Setup guide: docs/TOOLCHAINS.md"
    )
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint for Asmodeus."""
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    command = str(args.command)
    if command == "list":
        return _cmd_list()
    if command == "new":
        return _cmd_new(args)
    if command == "verify":
        return _cmd_verify(args)
    if command == "doctor":
        return _cmd_doctor()
    parser.print_help()
    return 1
