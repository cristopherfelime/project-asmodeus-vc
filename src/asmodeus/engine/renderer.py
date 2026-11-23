"""Deterministic template renderer supporting conditionals and variable substitution."""

import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from asmodeus.domain.models import ProjectSpec, RenderResult
from asmodeus.templates_registry import flavor_dir, overlay_dir

PLACEHOLDER_RE = re.compile(r"(?<!\$)\{\{([^{}]+)\}\}")
_IF_DIRECTIVE_RE = re.compile(r"^\{\{#if\s+([a-zA-Z0-9_]+)\s*\}\}$")
_BAD_IF_DIRECTIVE_RE = re.compile(r"^\{\{#if\b.*\}\}$")
_ELSE_DIRECTIVE_RE = re.compile(r"^\{\{\s*else\s*\}\}$")
_ENDIF_DIRECTIVE_RE = re.compile(r"^\{\{\s*/if\s*\}\}$")

__all__ = [
    "PLACEHOLDER_RE",
    "TemplateSyntaxError",
    "render_conditionals",
    "render_template_text",
    "scaffold_project",
    "substitute_variables",
]


class TemplateSyntaxError(ValueError):
    """Raised when a template contains invalid conditionals or unknown placeholders."""


@dataclass
class _ConditionalFrame:
    """Tracks one open {{#if ...}} block on the directive stack."""

    flag: str
    parent_active: bool
    branch_active: bool
    line_no: int
    saw_else: bool = False

    @property
    def is_active(self) -> bool:
        """Return True only when this block and all enclosing blocks are active."""
        return self.parent_active and self.branch_active


def render_conditionals(
    text: str,
    flags: Mapping[str, bool],
    *,
    source_name: str = "<template>",
) -> str:
    """Evaluate line-based {{#if <flag>}} / {{else}} / {{/if}} directives."""
    stack: list[_ConditionalFrame] = []
    output_lines: list[str] = []

    for line_no, raw_line in enumerate(text.splitlines(keepends=True), start=1):
        stripped = raw_line.strip()

        if_match = _IF_DIRECTIVE_RE.match(stripped)
        if if_match is not None:
            flag = if_match.group(1)
            if flag not in flags:
                msg = f"{source_name}:{line_no}: unknown conditional flag '{flag}'"
                raise TemplateSyntaxError(msg)
            parent_active = stack[-1].is_active if stack else True
            stack.append(
                _ConditionalFrame(
                    flag=flag,
                    parent_active=parent_active,
                    branch_active=bool(flags[flag]),
                    line_no=line_no,
                )
            )
            continue

        if _BAD_IF_DIRECTIVE_RE.match(stripped) is not None:
            msg = f"{source_name}:{line_no}: malformed #if directive '{stripped}'"
            raise TemplateSyntaxError(msg)

        if _ELSE_DIRECTIVE_RE.match(stripped) is not None:
            if not stack:
                msg = f"{source_name}:{line_no}: unexpected {{{{else}}}} without matching #if"
                raise TemplateSyntaxError(msg)
            top = stack[-1]
            if top.saw_else:
                msg = f"{source_name}:{line_no}: duplicate {{{{else}}}} for #if {top.flag}"
                raise TemplateSyntaxError(msg)
            top.saw_else = True
            top.branch_active = not top.branch_active
            continue

        if _ENDIF_DIRECTIVE_RE.match(stripped) is not None:
            if not stack:
                msg = f"{source_name}:{line_no}: unexpected {{{{/if}}}} without matching #if"
                raise TemplateSyntaxError(msg)
            stack.pop()
            continue

        if not stack or stack[-1].is_active:
            output_lines.append(raw_line)

    if stack:
        unclosed = stack[-1]
        msg = f"{source_name}:{unclosed.line_no}: unclosed #if {unclosed.flag}"
        raise TemplateSyntaxError(msg)

    return "".join(output_lines)


def _replace_placeholder(
    match: re.Match[str],
    context: Mapping[str, str],
    source_name: str,
) -> str:
    """Resolve one {{variable}} placeholder from the context mapping."""
    key = match.group(1).strip()
    if key not in context:
        msg = f"{source_name}: unknown template placeholder '{{{{{key}}}}}'"
        raise TemplateSyntaxError(msg)
    return context[key]


def substitute_variables(
    text: str,
    context: Mapping[str, str],
    *,
    source_name: str = "<template>",
) -> str:
    """Substitute {{variable}} placeholders while preserving ${{ ... }} expressions."""
    return PLACEHOLDER_RE.sub(
        lambda match: _replace_placeholder(match, context, source_name),
        text,
    )


def render_template_text(
    text: str,
    *,
    context: Mapping[str, str],
    flags: Mapping[str, bool],
    source_name: str = "<template>",
) -> str:
    """Evaluate conditionals first, then substitute template variables."""
    without_conditionals = render_conditionals(text, flags, source_name=source_name)
    return substitute_variables(without_conditionals, context, source_name=source_name)


def _render_relative_path(
    rel: Path,
    context: Mapping[str, str],
) -> tuple[Path, bool]:
    """Render variables in path segments and detect/strip .tmpl suffix."""
    source_name = rel.as_posix()
    rendered_parts: list[str] = []
    for part in rel.parts:
        rendered = substitute_variables(part, context, source_name=source_name)
        if not rendered or rendered in {".", ".."} or "/" in rendered or "\\" in rendered:
            msg = f"{source_name}: invalid rendered path segment '{rendered}'"
            raise TemplateSyntaxError(msg)
        rendered_parts.append(rendered)

    is_template = rendered_parts[-1].endswith(".tmpl")
    if is_template:
        stripped_name = rendered_parts[-1].removesuffix(".tmpl")
        if not stripped_name or stripped_name in {".", ".."}:
            msg = f"{source_name}: empty filename after removing .tmpl suffix"
            raise TemplateSyntaxError(msg)
        rendered_parts[-1] = stripped_name

    return Path(*rendered_parts), is_template


def _render_directory(
    source_dir: Path,
    target_dir: Path,
    *,
    context: Mapping[str, str],
    flags: Mapping[str, bool],
    written: set[str],
) -> None:
    """Render all files from source_dir into target_dir deterministically."""
    target_root = target_dir.resolve()
    source_files = sorted(
        (path for path in source_dir.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(source_dir).as_posix(),
    )

    for src_path in source_files:
        rel = src_path.relative_to(source_dir)
        dest_rel, is_template = _render_relative_path(rel, context)
        dest_path = (target_dir / dest_rel).resolve()
        if not dest_path.is_relative_to(target_root):
            msg = f"{rel.as_posix()}: rendered path escapes target directory"
            raise TemplateSyntaxError(msg)

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        if is_template:
            raw_text = src_path.read_text(encoding="utf-8")
            rendered_text = render_template_text(
                raw_text,
                context=context,
                flags=flags,
                source_name=rel.as_posix(),
            )
            dest_path.write_text(rendered_text, encoding="utf-8")
        else:
            dest_path.write_bytes(src_path.read_bytes())

        if dest_path.suffix == ".sh":
            dest_path.chmod(0o755)

        written.add(dest_rel.as_posix())


def scaffold_project(
    spec: ProjectSpec,
    target_dir: Path,
    *,
    templates_root: Path | None = None,
    force: bool = False,
) -> RenderResult:
    """Scaffold a project from its flavor and selected overlays into target_dir."""
    if target_dir.exists():
        if not target_dir.is_dir():
            msg = f"Target path exists and is not a directory: {target_dir}"
            raise FileExistsError(msg)
        if not force and any(target_dir.iterdir()):
            msg = f"Target directory is not empty: {target_dir} (use force=True to overwrite)"
            raise FileExistsError(msg)

    src_flavor = flavor_dir(spec.flavor, templates_root)
    src_overlays = [overlay_dir(overlay, templates_root) for overlay in spec.overlays]

    context = spec.template_context()
    flags = spec.condition_flags()
    written: set[str] = set()

    target_dir.mkdir(parents=True, exist_ok=True)
    _render_directory(src_flavor, target_dir, context=context, flags=flags, written=written)
    for src_overlay in src_overlays:
        _render_directory(src_overlay, target_dir, context=context, flags=flags, written=written)

    return RenderResult(
        target_dir=str(target_dir),
        flavor=spec.flavor,
        overlays=spec.overlays,
        files_written=tuple(sorted(written)),
    )
