"""AST architecture tests enforcing hexagonal domain purity."""

import ast
from pathlib import Path

_FORBIDDEN_NAMES = (
    "os",
    "pathlib",
    "sys",
    "subprocess",
    "shutil",
    "json",
    "urllib",
    "httpx",
    "sqlite3",
)
FORBIDDEN_MODULES: frozenset[str] = frozenset(_FORBIDDEN_NAMES)


def _is_datetime_now_call(node: ast.Call) -> bool:
    """Return True if an AST Call invokes datetime.now(...)."""
    func = node.func
    if not isinstance(func, ast.Attribute) or func.attr != "now":
        return False
    if isinstance(func.value, ast.Name):
        return func.value.id == "datetime"
    if isinstance(func.value, ast.Attribute):
        return func.value.attr == "datetime"
    return False


def test_domain_has_no_forbidden_imports_or_clock_calls() -> None:
    """Every module in src/asmodeus/domain/ must remain pure and side-effect free."""
    domain_dir = Path(__file__).resolve().parents[1] / "src" / "asmodeus" / "domain"
    py_files = sorted(domain_dir.rglob("*.py"))
    assert py_files, "Expected at least one Python file under src/asmodeus/domain/"

    for py_file in py_files:
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_mod = alias.name.split(".")[0]
                    assert root_mod not in FORBIDDEN_MODULES, (
                        f"Forbidden import '{alias.name}' in {py_file}"
                    )
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                root_mod = node.module.split(".")[0]
                assert root_mod not in FORBIDDEN_MODULES, (
                    f"Forbidden import from '{node.module}' in {py_file}"
                )
            elif isinstance(node, ast.Call):
                assert not _is_datetime_now_call(node), (
                    f"Forbidden datetime.now() call in {py_file}"
                )
