"""Pure domain models and identifier rules for Asmodeus."""

import re
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, field_validator

_SLUG_RE = re.compile(r"\A[a-z][a-z0-9-]{1,48}\Z")
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]")

__all__ = [
    "Flavor",
    "Overlay",
    "ProjectSpec",
    "RenderResult",
    "VerifyIssue",
    "VerifyReport",
]


class Flavor(StrEnum):
    """Supported base project flavors."""

    PYTHON_HEX = "python-hex"
    TS_WEBUI = "ts-webui"
    RUST_SERVICE = "rust-service"
    GO_SERVICE = "go-service"
    SCALA_SPARK = "scala-spark"


class Overlay(StrEnum):
    """Supported composable overlays."""

    AGENTS = "agents"
    COMPOSE = "compose"
    VM = "vm"
    GITHUB = "github"


class ProjectSpec(BaseModel):
    """Validated project specification used to drive rendering."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    project_name: str
    flavor: Flavor
    overlays: tuple[Overlay, ...] = ()
    study_mode: bool = False
    description: str = "A production-ready service scaffolded with Asmodeus."
    author: str = "Jeremie"
    github_user: str = "cristopherfelime"
    year: str = "2026"

    @field_validator("project_name")
    @classmethod
    def _validate_project_name(cls, value: str) -> str:
        """Ensure project_name is a valid kebab-case slug without edge hyphens."""
        if not _SLUG_RE.fullmatch(value) or value.endswith("-") or "--" in value:
            msg = (
                "project_name must be a kebab-case slug (2-49 chars, [a-z0-9-], "
                "starting with [a-z], no trailing or consecutive hyphens)"
            )
            raise ValueError(msg)
        return value

    @field_validator("overlays")
    @classmethod
    def _deduplicate_overlays(cls, value: tuple[Overlay, ...]) -> tuple[Overlay, ...]:
        """Deduplicate overlays while preserving caller order."""
        return tuple(dict.fromkeys(value))

    @property
    def package_name(self) -> str:
        """Return Python-compatible snake_case package identifier."""
        return self.project_name.replace("-", "_")

    @property
    def crate_name(self) -> str:
        """Return Rust-compatible snake_case crate identifier."""
        return self.project_name.replace("-", "_")

    @property
    def pascal_name(self) -> str:
        """Return PascalCase identifier derived from kebab-case segments."""
        return "".join(part.capitalize() for part in self.project_name.split("-"))

    @property
    def go_module(self) -> str:
        """Return canonical Go module import path."""
        return f"github.com/{self.github_user}/{self.project_name}"

    @property
    def scala_package(self) -> str:
        """Return valid single-segment lowercase Scala package identifier."""
        return _NON_ALNUM_RE.sub("", self.project_name.lower())

    @property
    def with_agents(self) -> bool:
        """Return True when the agents overlay is enabled."""
        return Overlay.AGENTS in self.overlays

    @property
    def with_compose(self) -> bool:
        """Return True when the compose overlay is enabled."""
        return Overlay.COMPOSE in self.overlays

    @property
    def with_vm(self) -> bool:
        """Return True when the vm overlay is enabled."""
        return Overlay.VM in self.overlays

    @property
    def with_github(self) -> bool:
        """Return True when the github overlay is enabled."""
        return Overlay.GITHUB in self.overlays

    def template_context(self) -> dict[str, str]:
        """Return template placeholder substitution mapping."""
        return {
            "project_name": self.project_name,
            "package_name": self.package_name,
            "crate_name": self.crate_name,
            "pascal_name": self.pascal_name,
            "go_module": self.go_module,
            "scala_package": self.scala_package,
            "description": self.description,
            "author": self.author,
            "github_user": self.github_user,
            "year": self.year,
        }

    def condition_flags(self) -> dict[str, bool]:
        """Return conditional directive flag mapping."""
        return {
            "study_mode": self.study_mode,
            "with_agents": self.with_agents,
            "with_compose": self.with_compose,
            "with_vm": self.with_vm,
            "with_github": self.with_github,
        }


class RenderResult(BaseModel):
    """Summary returned after scaffolding a target project directory."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    target_dir: str
    flavor: Flavor
    overlays: tuple[Overlay, ...]
    files_written: tuple[str, ...]


class VerifyIssue(BaseModel):
    """Single problem discovered while verifying a scaffolded project."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    path: str
    code: str
    message: str


class VerifyReport(BaseModel):
    """Structured result of post-scaffold project verification."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    target_dir: str
    ok: bool
    checked_files: int
    issues: tuple[VerifyIssue, ...]
