## Purpose
Define how Project Chimera will publish “Availability/Status” to the OpenClaw network safely and **auditable** (HITL + provenance + audit). This document is design-only and MUST NOT bypass the HITL requirements defined in `specs/functional.md`.

## Scope
In scope:
- Publishing Chimera operational status (“availability”) to the OpenClaw network.
- Defining a minimal status schema and invariants.
- Governance controls for enabling or disabling status publishing.

Out of scope:
- Implementing an OpenClaw client.
- Auto-publishing content to social platforms (still requires HITL approval).

## Integration Goals
- **Safety:** No externally observable action occurs without policy authorization and approval where required.
- **Traceability:** Every status update is spec-version bound and auditable.
- **Minimal disclosure:** Publish only operational state; never secrets, PII, or raw content.
- **Determinism:** Given the same health inputs and `spec_version`, derived status fields are stable.

## Status Payload (Proposed Contract)
A minimal payload Chimera publishes to OpenClaw:

```json
{
  "status_id": "string",
  "agent_id": "string",
  "timestamp": "2026-02-06T12:00:00Z",
  "availability": "AVAILABLE | DEGRADED | UNAVAILABLE",
  "capabilities": [
    "trend_discovery",
    "signal_ranking",
    "idea_generation",
    "hitl_review"
  ],
  "queue_depth": 0,
  "last_successful_run_at": "2026-02-06T10:30:00Z",
  "policy_state": {
    "hitl_enforced": true,
    "publishing_enabled": false
  },
  "spec_version": "commit-hash-or-tag",
  "digest": "string"
}
```
### Field Semantics

- `status_id`: Unique identifier for this status publication event. MUST be unique and immutable.
- `agent_id`: Stable identifier for the Chimera agent instance publishing the status.
- `timestamp`: UTC timestamp indicating when the status payload was generated.
- `availability`: Derived operational state of the system. MUST be one of `AVAILABLE`, `DEGRADED`, or `UNAVAILABLE`.
- `capabilities`: Declarative list of capabilities currently enabled and healthy for this agent.
- `queue_depth`: Integer representing the number of pending tasks awaiting processing at publish time.
- `last_successful_run_at`: UTC timestamp of the most recent successful end-to-end agent execution.
- `policy_state.hitl_enforced`: Boolean indicating whether human-in-the-loop approval is currently enforced.
- `policy_state.publishing_enabled`: Boolean indicating whether publishing is permitted by policy and approval.
- `spec_version`: Identifier (commit hash or tag) of the authoritative spec used to derive this payload.
- `digest`: Cryptographic digest of the canonical serialized payload for tamper-evidence.

## Invariants

* `spec_version` MUST be present on every payload.
* `availability` MUST be derived from documented health signals.
* Payload MUST NOT include secrets, tokens, raw trend data, content drafts, or PII.

## Health Signals (Availability Computation)

Availability is computed deterministically from:

* Trend ingestion health (recent successful ingestion events).
* Signal aggregation/ranking health.
* Idea generation health (recent artifact creation).
* Approval workflow health (ability to request and record approvals).
* Policy subsystem health (policy artifacts loadable and valid).

Example mapping:

* **AVAILABLE:** all critical subsystems healthy within the last X minutes.
* **DEGRADED:** at least one non-critical subsystem unhealthy.
* **UNAVAILABLE:** ingestion or policy/HITL subsystem unhealthy.

## Governance & Human-in-the-Loop (HITL)

Publishing status to OpenClaw is an **externally observable action**.

Rules:

* Status publishing MUST be disabled by default.
* Enabling status publishing MUST require:

  * a policy artifact authorizing the behavior, and
  * an operator approval event including `actor_id`, timestamp, justification, and `spec_version`.
* Disabling status publishing MUST also be recorded as an immutable governance event.

## Event & Audit Logging (MCP Alignment)

For every status publish attempt, Chimera MUST emit audit ledger events:

* `status.publish.requested`
* `status.publish.executed` OR `status.publish.rejected` OR `status.publish.failed`

Each event MUST include:

* `event_id`
* `timestamp` (UTC)
* `actor_id`
* `spec_version`
* `digest`
* `prev_event_id` where causal chaining applies

All events MUST be append-only and queryable.

## Failure Semantics & Rate Limits

* Fail-safe default: if health is uncertain, publish `DEGRADED` or suppress publishing (policy-defined).
* Rate limits MUST be enforced (e.g., no more than one status update per minute).
* Retries MUST be recorded; infinite retry loops are prohibited.

## Security Considerations

* OpenClaw credentials MUST use least privilege and be stored outside the repository.
* Signed payloads are recommended (implementation detail).
* Internal stack traces or error details MUST NOT appear in OpenClaw payloads.

## Testing Strategy (Future)

Planned contract-first tests:

* Schema validation for StatusPayload required fields.
* Determinism tests: identical health inputs + `spec_version` yield identical availability.
* Audit tests: correct event emission for requested/executed/failed publishing attempts.

## Acceptance Criteria

* Any published status payload can be traced to:

  * the authoritative `spec_version`,
  * the actor who enabled publishing, and
  * the corresponding audit events.
* No payload leaks secrets, PII, or content drafts.
* Governance, rate limits, and failure semantics are enforced and auditable.