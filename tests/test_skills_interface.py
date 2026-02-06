"""
Tests that assert skills exist and expose the standard `run(request: dict) -> dict`
interface.

These tests check that the skill package directories and contracts exist
under `skills/` and then (where possible) validate the runtime surface
(`run`) signature and output shape. These tests are intentionally written
to fail until the runtime implementations exist.
"""
from pathlib import Path
import os
import importlib
import inspect
import json
import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "skills"

SKILLS = (
    "skill_trend_fetcher",
    "skill_content_generator",
    "skill_engagement_manager",
)


def _skill_path(skill_name: str) -> Path:
    return SKILLS_DIR / skill_name


def test_skill_packages_and_contracts_exist():
    """Each required skill should exist as a directory and include a contract.json.

    This ensures repository-level artifacts (contracts & package layout)
    are present before runtime is implemented.
    """
    for skill in SKILLS:
        path = _skill_path(skill)
        assert path.exists() and path.is_dir(), f"Skill directory missing: {path}"
        contract = path / "contract.json"
        assert contract.exists(), f"Contract.json missing for skill {skill} at {contract}"


def test_run_signature_and_output_requirements():
    """Validate that each skill exposes `run(request)` and that a correct
    implementation would return a JSON-like dict including `spec_version`.

    These assertions assume a runtime implementation exists. They will fail
    (ImportError/AttributeError/AssertionError) until implementations are
    added — which is intentional for test-driven development.
    """
    sample_request = {
        "request_id": "t-req-1",
        "spec_version": "0.0-test"
    }

    for skill in SKILLS:
        # Attempt to import the runtime module. This will raise if not present.
        mod = importlib.import_module(f"skills.{skill}")

        # The runtime must expose a callable `run`.
        assert hasattr(mod, "run"), f"Skill {skill} must expose a 'run' function"
        fn = getattr(mod, "run")
        assert callable(fn), f"Skill {skill}.run must be callable"

        # The run function should accept a single positional argument (the request)
        sig = inspect.signature(fn)
        params = sig.parameters
        # Allow methods with single parameter; require exactly one non-var positional param
        non_var_params = [p for p in params.values() if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
        assert len(non_var_params) == 1, f"{skill}.run must accept exactly one positional request argument"

        # If the runtime is implemented, run it and validate the output is a dict containing spec_version
        result = fn(sample_request)
        assert isinstance(result, dict), f"{skill}.run must return a JSON-like dict"
        assert "spec_version" in result, f"{skill}.run output must include 'spec_version' for traceability"
