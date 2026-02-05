import json
from pathlib import Path


def test_contracts_exist():
    repo_root = Path(__file__).resolve().parents[1]
    skills_dir = repo_root / "skills"
    assert skills_dir.exists(), "skills directory is missing"

    contracts = list(skills_dir.glob("*/contract.json"))
    assert contracts, "No contract.json files found in skills/*"

    # Validate each contract is valid JSON
    for c in contracts:
        with c.open("r", encoding="utf-8") as fh:
            json.load(fh)
