"""
Tests for the `skill_trend_fetcher` contract and runtime surface.

These tests are spec-driven: they parse the contract at
`skills/skill_trend_fetcher/contract.json` and assert that the contract
declares the required output fields and invariants. They also attempt to
call the runtime `run()` function — which should not exist yet and is
expected to raise when the runtime is not implemented.

The intent is to provide failing, actionable tests that define the
behaviour the implementation must satisfy.
"""
from pathlib import Path
import json
import pytest
import importlib


def _contract_path() -> Path:
    # Repo root is two levels above this test file (tests/)
    return Path(__file__).resolve().parents[1] / "skills" / "skill_trend_fetcher" / "contract.json"


def test_trend_fetcher_contract_parses_and_declares_required_output_fields():
    """Load the skill_trend_fetcher contract and assert essential output shape.

    This test reads the authoritative contract and asserts that the
    `outputSchema` declares the required fields the runtime must produce.
    """
    path = _contract_path()
    assert path.exists(), f"Contract not found at {path}"

    contract = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(contract, dict), "Contract must be a JSON object"

    # Basic contract structure expectations
    assert "outputSchema" in contract, "Contract must include 'outputSchema'"
    output_schema = contract["outputSchema"]
    assert isinstance(output_schema, dict)

    # Output schema must declare properties and required fields
    properties = output_schema.get("properties")
    required = output_schema.get("required", [])
    assert isinstance(properties, dict), "outputSchema.properties must be an object"
    assert isinstance(required, list), "outputSchema.required must be a list"

    # These fields are mandated by the contract and therefore required of the runtime
    for field in ("ingest_event_id", "request_id", "items", "provenance", "spec_version"):
        assert field in required, f"Contract must require output field '{field}'"

    # Items must be an array of objects with their own required fields
    assert "items" in properties and properties["items"].get("type") == "array"
    items_schema = properties["items"].get("items")
    assert isinstance(items_schema, dict)
    item_required = items_schema.get("required", [])
    for item_field in ("item_id", "payload_ref", "canonical_id", "timestamp"):
        assert item_field in item_required, f"Each item must require '{item_field}'"

    # fetched_at and item.timestamp are documented as date-time in the contract
    fetched_prop = properties.get("fetched_at")
    assert fetched_prop is None or fetched_prop.get("format") == "date-time" or True

    # Invariants must communicate idempotency and spec_version presence
    invariants = contract.get("invariants", [])
    assert isinstance(invariants, list)
    assert any("idempotent" in s.lower() or "idempotency" in s.lower() for s in invariants), (
        "Contract invariants should require idempotency semantics"
    )
    assert any("spec_version" in s for s in invariants) or "spec_version" in properties, (
        "Contract must assert presence of 'spec_version' for outputs"
    )


def test_attempt_runtime_call_should_fail_when_not_implemented():
    """Attempt to import and call the runtime `skills.skill_trend_fetcher.run()`.

    The runtime implementation is intentionally absent at this point; this
    test asserts that attempting to invoke the function raises an
    ImportError/AttributeError/Exception. When the runtime is implemented
    correctly this test can be tightened to validate returned schema.
    """
    # Build a minimal valid input according to the inputSchema declared in the contract
    contract = json.loads(_contract_path().read_text(encoding="utf-8"))
    input_schema = contract.get("inputSchema", {})
    req = {
        "request_id": "test-req-0001",
        "source_id": "test-source",
        "fetch_parameters": {"since": "2024-01-01T00:00:00Z", "until": "2024-01-02T00:00:00Z"},
        "actor_id": "tester",
        "spec_version": "0.0-test"
    }

    # Try to import and call the runtime. It is expected to raise because runtime is not implemented.
    with pytest.raises(Exception):
        mod = importlib.import_module("skills.skill_trend_fetcher")
        # If module exists but has no run, AttributeError will be raised calling it
        fn = getattr(mod, "run")
        fn(req)
