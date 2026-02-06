# Project Chimera

## Project Overview
Project Chimera is a spec-driven codebase for building an autonomous, auditable AI influencer system. It is designed around safety, human-in-the-loop (HITL) governance, and end-to-end traceability.

This repository is **not a finished product**. It is a rigorously governed scaffold that is **READY TO BUILD** toward a production-grade system where all behavioral change is explicit, reviewable, and auditable.

---

## Repository Structure
- **specs/** — The single source of truth. Contains `_meta.md`, `functional.md`, and `technical.md` defining vision, governance, behavior, and contracts.
- **skills/** — Contract-first runtime skill definitions. Each skill includes a `contract.json` and a README describing its interface (e.g., trend fetching, content generation, engagement).
- **tests/** — Pytest-based tests authored from specs and contracts. Tests intentionally fail at this stage to define required runtime behavior (TDD).
- **scripts/** — Utility scripts such as lightweight spec alignment checks.
- **.github/workflows/** — CI workflows for automated spec checks, test execution, and governance gates.
- **Dockerfile** — Defines a reproducible containerized environment for tests and validation.
- **Makefile** — Standardized developer commands: `make setup`, `make test`, `make spec-check`.
- **.coderabbit.yaml** — AI review policy defining spec alignment and security review expectations.

> **Rule:** Specs drive implementation. Any behavioral or contract change must be reflected in `specs/` before code changes are accepted.

---

## Spec-Driven Development Model
- **`_meta.md`** — Repository-wide governance rules, safety constraints, and change management.
- **`functional.md`** — Capability-level behavior and acceptance criteria.
- **`technical.md`** — Technical contracts, schemas, invariants, and integration boundaries.

**Workflow rule:** change the spec first; tests and implementation follow.  
This enforces traceability: **spec → test → implementation**.

---

## Tooling & Skills Strategy
- **Developer tooling:** MCP telemetry, CI (GitHub Actions), Docker, and Makefile targets enforce consistency and governance.
- **Runtime skills:** Contract-bound modules (e.g., trend fetcher, content generator, engagement manager). Implementations must emit deterministic outputs including provenance and `spec_version`.

Contract-first design ensures behavior is explicit, testable, and reviewable before any automation occurs.

---

## Testing Strategy (True TDD)
Tests are derived directly from specs and contracts. At this stage, tests are **expected to fail**:

- Failing tests define the “empty slots” the agent must fill.
- They specify required signatures, outputs, and invariants.
- This prevents informal or undocumented behavior from entering the system.

Passing tests will only be expected once runtime implementations exist.

---

## Containerization & Automation
- The **Dockerfile** encapsulates a minimal, reproducible Python environment.
- The **Makefile** provides standardized commands:
  - `make setup` — install local dependencies
  - `make test` — run pytest in a controlled environment (Docker where available)
  - `make spec-check` — validate spec and contract alignment

Docker is optional for local development but required for reproducible environments and CI.

---

## CI/CD & AI Governance
GitHub Actions workflows in `.github/workflows/` enforce:
- Spec alignment checks
- Test execution
- Policy and governance gates

The **AI review policy** (`.coderabbit.yaml`) instructs automated reviewers to:
- Verify alignment with specs
- Flag security vulnerabilities and unsafe patterns
- Enforce least-privilege and HITL principles

All behavior-affecting changes require human review before merge or release.

---

## MCP Telemetry
Tenx MCP Sense is used for AI fluency and operational telemetry.

- Telemetry is limited to **metadata and metrics**
- **No chain-of-thought or internal reasoning** is logged
- Policies emphasize privacy, minimal retention, and auditability

---

## Known Limitations
- Runtime skill implementations are intentionally missing; failing tests are expected.
- GitHub Actions execution may be blocked by temporary account billing restrictions, though workflows are fully configured.
- Docker may be unavailable on some local machines; the repository remains usable without containers for inspection and review.

---

## Status
**READY TO BUILD**

This submission provides the governed foundation for building and operating an autonomous AI system safely and audibly. No generated video content is included; the deliverable is the repository itself.

---

## Getting Started (Quick)
```bash
make setup
make test
make spec-check