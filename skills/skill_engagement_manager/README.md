# Skill: skill_engagement_manager

Purpose
- The `skill_engagement_manager` skill proposes engagement actions (e.g., scheduling, targeting, campaign metadata) for candidate artifacts. It MUST treat engagement actions as externally observable and MUST NOT execute them. All proposals MUST be gated by approval references and human-in-the-loop workflows.

It does NOT:
- Execute publishing, scheduling, or direct network actions.

Input Contract (JSON)
```json
{
  "request_id": "string",            // idempotency token (MUST)
  "artifact_id": "string",           // content artifact id (MUST)
  "candidate_context": {               // optional context object
    "target_platforms": ["string"],
    "audience_constraints": {"string":"string"}
  },
  "actor_id": "string",
  "spec_version": "string",
  "approval_reference": "string|null" // REQUIRED for execution (MUST be null for proposals)
}
```

Output Contract (JSON)
```json
{
  "proposal_id": "string",           // unique id for this proposal (MUST)
  "request_id": "string",            // echoes input request_id (MUST)
  "artifact_id": "string",
  "proposed_actions": [                // array of proposed external actions (MUST)
    {
      "action_id": "string",
      "action_type": "string",      // e.g., "schedule", "publish", "promote"
      "target": "string",
      "scheduled_time": "string|null",
      "estimated_impact": {"metric":"number"},
      "approval_required": true
    }
  ],
  "provenance": ["string"],          // event ids and inputs used to build proposal
  "spec_version": "string"
}
```

Determinism & Invariants
- For identical `request_id`, `artifact_id`, `candidate_context`, and `spec_version`, the proposal MUST be stable and idempotent.
- Proposed actions MUST include `approval_required: true`.

Error Handling
- Errors MUST follow `ErrorObject` from `specs/technical.md`.
- Common error codes: `VALIDATION_ERROR`, `PROPOSAL_GENERATION_ERROR`, `AUTHZ_FAILURE`.

Governance & Execution Guardrails
- The skill MUST NOT execute any `proposed_actions`; it MUST return proposals only.
- Any attempt to execute a proposed action MUST require a valid `approval_reference` pointing to an `ApprovalDecision` with `approve` result and appropriate role; execution is out-of-skill responsibility and MUST be audited by MCP.

Audit & MCP
- Proposals MUST include `provenance` chains and `spec_version`. All proposal events MUST be logged to the MCP audit ledger with event ids returned or referenced in the `provenance` array.
# skill_engagement_manager
