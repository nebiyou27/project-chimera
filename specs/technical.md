## Project Chimera — Technical Contracts

### Outline
- Overview
- Data Model Definitions
- API / Interface Contracts
  - Trend ingestion
  - Signal aggregation
  - Idea artifact generation
  - Approval workflows
  - Externally observable actions
- Event & Audit Record Schemas (MCP)
- Error & Failure Contracts
- Validation & Determinism Rules
- Security & Access-Control Interfaces (conceptual)
- Spec-Version Binding Requirements

---

### Overview
This document defines normative, machine-readable contracts that implementations MUST satisfy. Contracts are expressed as JSON input/output schemas and declarative invariants. Implementations and tests MUST treat these contracts as authoritative. All language in this document using MUST, MUST NOT, SHOULD, MAY is normative.

Notes:
- All identifiers referenced in these contracts are opaque strings that conform to a project identifier scheme (URN or UUID) and MUST be globally unique within the system.
- All timestamps MUST be ISO 8601 extended format in UTC (e.g., `2026-02-05T15:04:05Z`).
- The field `spec_version` is REQUIRED on all artifacts and events and binds the artifact to the authoritative spec snapshot.

---

## Data Model Definitions (conceptual)

Common primitives
- id: string (opaque unique identifier)
- timestamp: string (ISO 8601 UTC)
- spec_version: string (authoritative spec identifier; e.g., commit hash or version tag)
- actor_id: string (role-qualified actor identifier; human or agent)
- digest: string (cryptographic digest of referenced payload; representation algorithm is implementation detail but presence is required)

Common invariants
- Every persistent record MUST include `id`, `timestamp`, `spec_version`, and `digest` (or a reason field explaining absence).
- `id` values MUST be stable and immutable once created.

---

## API / Interface Contracts

Note: Each contract below is presented as a JSON object schema (conceptual). Field types are either `string`, `number`, `object`, `array`, or `boolean`. `required` lists fields that MUST be present.

### 1) Trend Ingestion — Input (ingest request)
Contract: IngestRequest (JSON object)
- Required fields:
  - `request_id` (string): unique id for the ingestion request.
  - `source_id` (string): canonical identifier of the source.
  - `received_at` (timestamp): time the ingestion system received the payload.
  - `payload_ref` (object): reference to the raw payload. See payload_ref contract.
  - `spec_version` (string): active spec version.

payload_ref (object):
- Required fields:
  - `type` (string): short type label for payload (e.g., "social_post", "feed_batch").
  - `uri` (string): location pointer for the raw payload (opaque to spec; implementations MUST provide a retrievable reference).
  - `digest` (string): digest of raw payload content.
  - `size` (number): byte size of the payload.

Invariants & Validation Rules:
- `request_id`, `source_id`, `uri`, and `digest` MUST be non-empty.
- `received_at` MUST be <= server processing time and MUST be in UTC.

Expected Response (IngestResponse):
- `request_id` (string)
- `ingest_event_id` (string) — id of created ingestion event
- `status` (string) — one of `queued`, `accepted`, `rejected`
- `reason` (string) — required when `status` is `rejected`
- `timestamp` (timestamp)
- `spec_version` (string)

Failure response MUST follow Error Contract (see below).

### 2) Signal Aggregation — Input / Output

Input: AggregationRequest
- Required fields:
  - `request_id` (string)
  - `input_event_ids` (array[string]) — list of ingestion event ids to aggregate (ORDERED as provided)
  - `aggregation_window` (object): `{ "start": timestamp, "end": timestamp }`
  - `spec_version` (string)

Output: AggregationResponse
- Required fields:
  - `request_id` (string)
  - `aggregation_id` (string)
  - `generated_at` (timestamp)
  - `trend_candidates` (array[object]) — ordered list of candidates; order is deterministic and significant.

trend_candidate (object) fields (required):
- `candidate_id` (string)
- `score` (number) — numeric score; higher is more significant.
- `primary_tag` (string)
- `contributing_event_ids` (array[string]) — list of ingestion event ids that contributed
- `provenance_summary` (object) — minimal provenance descriptor
- `spec_version` (string)

Invariants & Validation Rules:
- `aggregation_id` and each `candidate_id` MUST be unique.
- `trend_candidates` array ordering MUST be deterministic given identical inputs and `spec_version`.

### 3) Idea Artifact Generation — Output Contract

IdeaArtifact (object) — required fields:
- `artifact_id` (string)
- `candidate_id` (string) — linked trend candidate id
- `created_at` (timestamp)
- `created_by` (actor_id)
- `title` (string)
- `description` (string)
- `variants` (array[object]) — non-empty; each variant contains `variant_id`, `text`, and `metadata`.
- `metadata` (object) — includes keys: `target_platforms` (array[string]), `estimated_risk_score` (number), `tags` (array[string])
- `provenance` (array[object]) — ordered chain of provenance entries referencing source event ids and processing steps
- `spec_version` (string)

variant (object) required fields:
- `variant_id` (string)
- `text` (string)
- `metadata` (object)

Invariants & Validation Rules:
- `artifact_id` MUST be unique and immutable.
- `variants` array ordering MUST be deterministic and preserved.
- `estimated_risk_score` MUST be a numeric value in the inclusive range [0.0, 1.0].

Storage & Retrieval Response:
- On creation, system MUST emit an ArtifactCreatedResponse containing `artifact_id`, `created_at`, and `spec_version`.

### 4) Approval Workflow — Input / Output

ApprovalRequest (object) — required fields:
- `approval_request_id` (string)
- `artifact_id` (string)
- `requested_by` (actor_id)
- `requested_at` (timestamp)
- `required_approver_role` (string)
- `policy_reference` (string) — id of policy artifact used to determine approval level
- `expiry` (timestamp) — optional, if present must be > `requested_at`
- `spec_version` (string)

ApprovalDecision (object) — required fields:
- `approval_request_id` (string)
- `decision_id` (string)
- `artifact_id` (string)
- `approver_id` (actor_id)
- `decision` (string) — one of `approve`, `reject`, `modify`, `escalate`
- `decision_timestamp` (timestamp)
- `justification` (string) — MUST be present and at least 20 characters unless `decision` is `approve` and policy allows minimal justification; policy_reference MUST document allowance.
- `spec_version` (string)

Outcome Response: ApprovalOutcome
- `approval_request_id`, `decision_id`, `artifact_id`, `result_state` (one of `Approved`, `Rejected`, `Escalated`, `Modified`), `decision_timestamp`, `spec_version`.

Invariants & Validation Rules:
- An `ApprovalDecision` MUST reference a valid `ApprovalRequest` by `approval_request_id`.
- If `decision` == `escalate`, `escalation_targets` array MUST be present in the outcome metadata.

### 5) Externally Observable Actions — Action Command & Event

ActionCommand (object) — required fields:
- `action_id` (string)
- `artifact_id` (string)
- `commanded_by` (actor_id)
- `commanded_at` (timestamp)
- `action_type` (string) — e.g., `publish`, `schedule`, `withdraw`
- `target_endpoint` (string) — opaque identifier for external target
- `approval_reference_id` (string) — id of ApprovalDecision that authorizes action; MUST be present unless policy explicitly permits otherwise and `policy_reference` field is present.
- `spec_version` (string)

ActionEvent (object) — required fields (emitted after attempted execution):
- `action_id` (string)
- `action_event_id` (string)
- `artifact_id` (string)
- `actor_id` (actor_id)
- `action_type` (string)
- `target_endpoint` (string)
- `approval_reference_id` (string)
- `status` (string) — one of `pending`, `executed`, `failed`, `rejected`
- `result` (object) — MAY include `external_id`, `response_code`, `response_message` (opaque)
- `timestamp` (timestamp)
- `spec_version` (string)

Invariants & Validation Rules:
- An `ActionCommand` MUST NOT be executed unless a valid `approval_reference_id` exists and maps to an `approve` decision with required role, unless `policy_reference` explicitly allows auto-action and that `policy_reference` is recorded.
- `ActionEvent.status` transitions and final states MUST be recorded as event records in the audit ledger.

---

## Event & Audit Record Schemas (MCP)

All event records MUST be JSON objects containing these core fields (EventRecord):
- `event_id` (string) — unique id for event
- `event_type` (string) — e.g., `ingest`, `aggregate`, `artifact.created`, `approval.requested`, `approval.decision`, `action.event`, `state.transition`, `error`.
- `timestamp` (timestamp)
- `actor_id` (string)
- `spec_version` (string)
- `payload_ref` (object) — minimal reference to the payload affected (fields: `type`, `id`, `digest`)
- `prev_event_id` (string|null) — id of prior related event for causal chaining; null if root
- `digest` (string) — digest over canonical serialization of event payload
- `tamper_evidence` (object) — MUST include at least `digest` and SHOULD include `chain_digest` indicating chaining scheme

Event Store Invariants:
- Event records MUST be append-only and ordered by `timestamp`; ordering ties MUST be resolved by `event_id` ordering.
- Event queries MUST be able to filter by `event_type`, `artifact_id` (via payload_ref.id), `actor_id`, `spec_version`, and time ranges.

Provenance Chain Requirements
- Every artifact (e.g., IdeaArtifact) MUST include a `provenance` array referencing event ids that produced or materially affected the artifact. The provenance array MUST be ordered from earliest to latest.

---

## Error & Failure Response Contracts

ErrorObject (required structure for all error responses):
- `error_id` (string) — unique id for the error occurrence
- `error_code` (string) — short machine identifier (e.g., `INGEST_DUPLICATE`, `AUTHZ_FAILURE`)
- `message` (string) — human-readable summary
- `details` (object|null) — optional structured details; if present, fields MUST be deterministic and documented per API
- `timestamp` (timestamp)
- `related_event_id` (string|null) — if error relates to an event
- `spec_version` (string)

Clients MUST expect ErrorObject when operations fail. Error codes MUST be enumerated in integration tests.

Failure Semantics
- For transient failures, responses SHOULD include retry metadata in `details` (e.g., `retry_after_seconds`).
- For permanent rejections, `details` MUST include `reason` and, where applicable, `remediation` guidance.

---

## Validation & Determinism Rules

- Deterministic serialization: Implementations MUST use a canonical JSON serialization for producing `digest` values and for deterministic comparisons. Canonical serialization MUST specify UTF-8 encoding and lexicographic ordering of object keys.
- Deterministic ordering: Wherever arrays represent ordered outputs (e.g., `trend_candidates`, `variants`), the ordering MUST be stable and reproducible given identical inputs and `spec_version`.
- Idempotency: APIs that create resources MUST support idempotent requests using `request_id`/`request_token` semantics; repeated identical requests with the same `request_id` MUST return the same resource id and not create duplicates.
- Input validation: All APIs MUST validate required fields and types and return `ErrorObject` on validation failure with `error_code` `VALIDATION_ERROR` and `details` listing missing or invalid fields.

---

## Security & Access-Control Interfaces (conceptual)

- Authentication and authorization are out of scope for concrete methods, but contracts REQUIRE the following conceptual interfaces:
  - `actor_id` MUST map to an authenticated identity and associated role(s).
  - Each API call and event record MUST record `actor_id` and the effective role used for the action.
  - Access checks MUST be determinable given an actor's role and policy artifacts; authorization failures MUST return `ErrorObject` with `error_code` `AUTHZ_FAILURE`.

---

## Spec-Version Binding Requirements

- Every artifact, event, and error response MUST include `spec_version`.
- Implementations MUST record the authoritative `spec_version` used to interpret contracts and policy artifacts at the time of action. Tests and audits MUST be able to reproduce behavior by replaying inputs against the recorded `spec_version`.

---

This technical contract document is authoritative for implementation interfaces, test fixtures, and audit expectations. Any change to these contracts MUST be made via an approved `specs/` change and MUST include updated machine-readable schema examples and test fixtures.
# Technical Spec
