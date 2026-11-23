"""Post-scaffold verification checks for generated projects."""

from pathlib import Path

from asmodeus.domain.models import VerifyIssue, VerifyReport
from asmodeus.engine.renderer import PLACEHOLDER_RE

_ALLOWED_ENV_NAMES = (".env.example", ".env.compose.example")
ALLOWED_ENV_FILES: frozenset[str] = frozenset(_ALLOWED_ENV_NAMES)

_IGNORED_DIR_NAMES = (
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
    "target",
)
IGNORED_DIRS: frozenset[str] = frozenset(_IGNORED_DIR_NAMES)

__all__ = [
    "ALLOWED_ENV_FILES",
    "IGNORED_DIRS",
    "verify_project",
]


def verify_project(target_dir: Path) -> VerifyReport:
    """Verify baseline hygiene and absence of unrendered template placeholders."""
    if not target_dir.is_dir():
        issue = VerifyIssue(
            path=".",
            code="missing-target",
            message=f"Target directory does not exist: {target_dir}",
        )
        return VerifyReport(
            target_dir=str(target_dir),
            ok=False,
            checked_files=0,
            issues=(issue,),
        )

    issues: list[VerifyIssue] = []

    if not (target_dir / ".gitignore").is_file():
        issues.append(
            VerifyIssue(
                path=".gitignore",
                code="missing-gitignore",
                message="Missing required .gitignore file.",
            )
        )

    if not (target_dir / "README.md").is_file():
        issues.append(
            VerifyIssue(
                path="README.md",
                code="missing-readme",
                message="Missing required README.md file.",
            )
        )

    checked_files = 0
    candidate_files = sorted(
        (path for path in target_dir.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(target_dir).as_posix(),
    )

    for file_path in candidate_files:
        rel = file_path.relative_to(target_dir)
        if any(part in IGNORED_DIRS for part in rel.parts[:-1]):
            continue

        checked_files += 1
        rel_posix = rel.as_posix()
        name = file_path.name

        if name == ".env" or (name.startswith(".env.") and name not in ALLOWED_ENV_FILES):
            issues.append(
                VerifyIssue(
                    path=rel_posix,
                    code="forbidden-env-file",
                    message=f"Forbidden secret environment file present: {rel_posix}",
                )
            )

        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for line_no, line in enumerate(content.splitlines(), start=1):
            for match in PLACEHOLDER_RE.finditer(line):
                token = match.group(1)
                issues.append(
                    VerifyIssue(
                        path=rel_posix,
                        code="unrendered-placeholder",
                        message=f"Line {line_no}: unrendered placeholder '{{{{{token}}}}}'",
                    )
                )

    return VerifyReport(
        target_dir=str(target_dir),
        ok=len(issues) == 0,
        checked_files=checked_files,
        issues=tuple(issues),
    )
