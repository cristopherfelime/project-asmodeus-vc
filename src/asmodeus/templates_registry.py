"""Template root discovery for flavors and composable overlays."""

from pathlib import Path

from asmodeus.domain.models import Flavor, Overlay

__all__ = [
    "flavor_dir",
    "list_flavors",
    "list_overlays",
    "overlay_dir",
    "repo_templates_root",
]


def repo_templates_root() -> Path:
    """Return the repository-level templates directory."""
    return Path(__file__).resolve().parents[2] / "templates"


def _discover_subdirs(base_dir: Path, fallback: list[str]) -> list[str]:
    """List sorted non-hidden subdirectories or fall back to domain enum names."""
    if not base_dir.is_dir():
        return fallback
    found: list[str] = []
    for entry in base_dir.iterdir():
        if entry.is_dir() and not entry.name.startswith("."):
            found.append(entry.name)
    return sorted(found) if found else fallback


def list_flavors(templates_root: Path | None = None) -> list[str]:
    """Return available flavor template identifiers."""
    root = templates_root if templates_root is not None else repo_templates_root()
    fallback = sorted(flavor.value for flavor in Flavor)
    return _discover_subdirs(root / "flavors", fallback)


def list_overlays(templates_root: Path | None = None) -> list[str]:
    """Return available overlay template identifiers."""
    root = templates_root if templates_root is not None else repo_templates_root()
    fallback = sorted(overlay.value for overlay in Overlay)
    return _discover_subdirs(root / "overlays", fallback)


def flavor_dir(flavor: Flavor, templates_root: Path | None = None) -> Path:
    """Resolve and validate the directory for a base flavor."""
    root = templates_root if templates_root is not None else repo_templates_root()
    candidate = root / "flavors" / flavor.value
    if not candidate.is_dir():
        msg = f"Flavor template directory not found: {candidate}"
        raise FileNotFoundError(msg)
    return candidate


def overlay_dir(overlay: Overlay, templates_root: Path | None = None) -> Path:
    """Resolve and validate the directory for an overlay."""
    root = templates_root if templates_root is not None else repo_templates_root()
    candidate = root / "overlays" / overlay.value
    if not candidate.is_dir():
        msg = f"Overlay template directory not found: {candidate}"
        raise FileNotFoundError(msg)
    return candidate
