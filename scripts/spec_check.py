#!/usr/bin/env python3
"""
Lightweight spec checker used by `make spec-check`.

Checks performed:
- `specs/` directory exists
- Each skill subdirectory under `skills/` contains a valid `contract.json`
- Each contract JSON contains the string `spec_version` somewhere in its keys

This tool is intentionally simple and fails fast to help developers
discover missing or malformed contract artifacts.
"""
from pathlib import Path
import sys
import json


ROOT = Path(__file__).resolve().parents[1]
ERRORS = []


def check_specs_dir():
    specs = ROOT / "specs"
    if not specs.exists() or not specs.is_dir():
        ERRORS.append(f"Missing specs directory: {specs}")


def find_contracts():
    skills_dir = ROOT / "skills"
    if not skills_dir.exists() or not skills_dir.is_dir():
        ERRORS.append(f"Missing skills directory: {skills_dir}")
        return []
    contracts = []
    for child in skills_dir.iterdir():
        if child.is_dir():
            c = child / "contract.json"
            if not c.exists():
                ERRORS.append(f"Missing contract.json for skill: {child.name}")
            else:
                contracts.append(c)
    return contracts


def contains_spec_version(obj):
    """Recursively search for the key 'spec_version' in JSON-like objects."""
    if isinstance(obj, dict):
        if "spec_version" in obj:
            return True
        return any(contains_spec_version(v) for v in obj.values())
    if isinstance(obj, list):
        return any(contains_spec_version(i) for i in obj)
    return False


def validate_contracts(contracts):
    for c in contracts:
        try:
            data = json.loads(c.read_text(encoding="utf-8"))
        except Exception as e:
            ERRORS.append(f"Invalid JSON in {c}: {e}")
            continue

        if not contains_spec_version(data):
            ERRORS.append(f"contract.json missing 'spec_version' key (nested) in {c}")


def main():
    check_specs_dir()
    contracts = find_contracts()
    validate_contracts(contracts)

    if ERRORS:
        print("SPEC CHECK FAILED:\n")
        for e in ERRORS:
            print(f" - {e}")
        sys.exit(2)

    print("SPEC CHECK PASSED: specs/ present and contracts contain spec_version")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
