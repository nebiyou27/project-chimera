# Project Chimera — Copilot Instructions

## Prime Directive (Non-Negotiable)
NEVER generate or modify implementation code without consulting `specs/` first.
The `specs/` directory is the single source of truth.

## Spec-Driven Development
- All behavior, contracts, and acceptance criteria are defined in `specs/`.
- Any behavioral change requires a spec change first.
- Tests may intentionally fail (TDD) until implementations exist.

## Human-in-the-Loop (HITL)
- No externally observable action (publishing, scheduling, network calls)
  may occur without explicit human approval.
- Approval decisions must be auditable.

## Governance & Safety
- Prefer least privilege and deterministic outputs.
- Do not bypass policy, security, or governance rules.
- Favor dry-runs and explainable behavior.

## Telemetry & Privacy
- Tenx MCP Sense may be used for AI fluency and operational telemetry.
- Do NOT log or expose chain-of-thought or internal reasoning.

## Assistant Behavior
- Answer using repository context.
- Reference relevant `specs/` when explaining behavior.
- If uncertain, ask for clarification rather than guessing.