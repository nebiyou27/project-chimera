#!/usr/bin/env python3
"""
Lightweight spec checker used by `make spec-check`.

Checks performed:
- `specs/` directory exists
- Core spec files exist: `_meta.md`, `functional.md`, `technical.md`
- Each skill subdirectory under `skills/` contains a valid `contract.json`
- Each contract JSON contains the key `spec_version` somewhere (nested allowed)

This tool is intentionally simple and fails fast to help developers
discover missing or malformed spec/contract artifacts.
"""

from __future__ import annotations

from pathlib import Path
import json
import sys
from typing import Any, List


ROOT = Path(__file__).resolve().parents[1]
ERRORS: List[str] = []


def error(msg: str) -> None:
    ERRORS.append(msg)


def check_specs_dir() -> None:
    specs = ROOT / "specs"
    if not specs.exists() or not specs.is_dir():
        error(f"Missing specs directory: {specs}")


def check_core_spec_files() -> None:
    # Keep this aligned with your repo's expected spec filenames.
    required = ["_meta.md", "functional.md", "technical.md"]
    for name in required:
        p = ROOT / "specs" / name
        if not p.exists():
            error(f"Missing required spec file: {p}")


def find_contracts() -> List[Path]:
    skills_dir = ROOT / "skills"
    if not skills_dir.exists() or not skills_dir.is_dir():
        error(f"Missing skills directory: {skills_dir}")
        return []

    contracts: List[Path] = []
    for child in skills_dir.iterdir():
        if not child.is_dir():
            continue

        # Ignore Python cache directories or other non-skill dirs if present
        if child.name in {"__pycache__", ".pytest_cache"}:
            continue

        c = child / "contract.json"
        if not c.exists():
            # Only require contract.json for directories that look like skills
            # (your repo uses skill_* naming)
            if child.name.startswith("skill_"):
                error(f"Missing contract.json for skill: {child.name}")
            continue

        contracts.append(c)

    return contracts


def contains_spec_version(obj: Any) -> bool:
    """Recursively search for the key 'spec_version' in JSON-like objects."""
    if isinstance(obj, dict):
        if "spec_version" in obj:
            return True
        return any(contains_spec_version(v) for v in obj.values())
    if isinstance(obj, list):
        return any(contains_spec_version(i) for i in obj)
    return False


def validate_contracts(contracts: List[Path]) -> None:
    for c in contracts:
        try:
            data = json.loads(c.read_text(encoding="utf-8"))
        except Exception as e:
            error(f"Invalid JSON in {c}: {e}")
            continue

        if not isinstance(data, dict):
            error(f"contract.json must be a JSON object (top-level) in {c}")
            continue

        if not contains_spec_version(data):
            error(f"contract.json missing 'spec_version' key (nested) in {c}")


def main() -> int:
    check_specs_dir()
    # Only check core spec files if specs/ exists (avoid duplicate noise)
    if (ROOT / "specs").exists():
        check_core_spec_files()

    contracts = find_contracts()
    validate_contracts(contracts)

    if ERRORS:
        print("SPEC CHECK FAILED:\n")
        for e in ERRORS:
            print(f" - {e}")
        return 2

    print("SPEC CHECK PASSED: specs present, core specs exist, and contracts contain spec_version")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())