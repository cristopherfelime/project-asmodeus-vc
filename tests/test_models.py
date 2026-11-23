"""Unit and property tests for pure domain models."""

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from asmodeus.domain.models import Flavor, Overlay, ProjectSpec

_ALPHA = "abcdefghijklmnopqrstuvwxyz"
_ALNUM = "abcdefghijklmnopqrstuvwxyz0123456789"
_SEGMENT = st.text(alphabet=_ALNUM, min_size=1, max_size=10)
_SLUG_STRATEGY = st.tuples(
    st.sampled_from(_ALPHA),
    _SEGMENT,
    st.lists(_SEGMENT, min_size=0, max_size=3),
)


@pytest.mark.parametrize(
    "slug",
    [
        "ab",
        "my-app",
        "service-2",
        "a-1-b-2",
        "a" * 49,
    ],
)
def test_valid_project_slugs(slug: str) -> None:
    """Valid kebab-case slugs construct ProjectSpec cleanly."""
    spec = ProjectSpec(project_name=slug, flavor=Flavor.PYTHON_HEX)
    assert spec.project_name == slug


@pytest.mark.parametrize(
    "bad_slug",
    [
        "",
        "a",
        "a" * 50,
        "My-App",
        "1app",
        "-app",
        "app-",
        "app--one",
        "app_one",
        "app\n",
    ],
)
def test_invalid_project_slugs_rejected(bad_slug: str) -> None:
    """Invalid slugs raise pydantic.ValidationError."""
    with pytest.raises(ValidationError):
        ProjectSpec(project_name=bad_slug, flavor=Flavor.PYTHON_HEX)


def test_derived_identifiers_and_context() -> None:
    """Derived language identifiers and template context match specification."""
    spec = ProjectSpec(
        project_name="billing-core-v2",
        flavor=Flavor.RUST_SERVICE,
        overlays=(Overlay.AGENTS, Overlay.GITHUB, Overlay.AGENTS),
        study_mode=True,
        description="Ledger core",
        author="Jeremie",
        github_user="cristopherfelime",
        year="2026",
    )

    assert spec.overlays == (Overlay.AGENTS, Overlay.GITHUB)
    assert spec.package_name == "billing_core_v2"
    assert spec.crate_name == "billing_core_v2"
    assert spec.pascal_name == "BillingCoreV2"
    assert spec.go_module == "github.com/cristopherfelime/billing-core-v2"
    assert spec.scala_package == "billingcorev2"
    assert spec.with_agents is True
    assert spec.with_compose is False
    assert spec.with_vm is False
    assert spec.with_github is True

    assert spec.template_context() == {
        "project_name": "billing-core-v2",
        "package_name": "billing_core_v2",
        "crate_name": "billing_core_v2",
        "pascal_name": "BillingCoreV2",
        "go_module": "github.com/cristopherfelime/billing-core-v2",
        "scala_package": "billingcorev2",
        "description": "Ledger core",
        "author": "Jeremie",
        "github_user": "cristopherfelime",
        "year": "2026",
    }
    assert spec.condition_flags() == {
        "study_mode": True,
        "with_agents": True,
        "with_compose": False,
        "with_vm": False,
        "with_github": True,
    }


def test_project_spec_is_frozen_and_forbids_extras() -> None:
    """ProjectSpec rejects attribute mutation and unknown extra fields."""
    spec = ProjectSpec(project_name="sample-api", flavor=Flavor.GO_SERVICE)
    field_name = "project_name"
    with pytest.raises(ValidationError):
        setattr(spec, field_name, "other-api")

    with pytest.raises(ValidationError):
        ProjectSpec.model_validate(
            {
                "project_name": "sample-api",
                "flavor": "go-service",
                "unexpected_field": True,
            }
        )


@given(parts=_SLUG_STRATEGY)
def test_hypothesis_valid_slugs(parts: tuple[str, str, list[str]]) -> None:
    """Property test: any generated valid slug yields coherent derived identifiers."""
    first, head_rest, tail = parts
    slug = "-".join([f"{first}{head_rest}", *tail])
    spec = ProjectSpec(project_name=slug, flavor=Flavor.SCALA_SPARK)

    assert spec.project_name == slug
    assert spec.package_name == slug.replace("-", "_")
    assert spec.crate_name == slug.replace("-", "_")
    assert spec.pascal_name.isalnum()
    assert spec.pascal_name[0].isupper()
    assert spec.go_module == f"github.com/cristopherfelime/{slug}"
    assert spec.scala_package == slug.replace("-", "")
