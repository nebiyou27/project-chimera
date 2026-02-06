# Project Chimera — Technical Contracts

## Outline
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

## Overview
This document defines normative, machine-readable technical contracts that all
implementations of Project Chimera MUST satisfy. Contracts are expressed as JSON
input/output schemas, declarative invariants, and validation rules.

All language in this document using **MUST**, **MUST NOT**, **SHOULD**, or **MAY**
is normative.

Notes:
- All identifiers referenced in these contracts are opaque strings that conform
  to a project-wide identifier scheme (e.g., URN or UUID) and MUST be globally
  unique within the system.
- All timestamps MUST be in ISO 8601 extended format and expressed in UTC
  (e.g., `2026-02-05T15:04:05Z`).
- The field `spec_version` is REQUIRED on all artifacts, events, and error
  responses and binds each record to the authoritative specification snapshot.

---

## Data Model Definitions (Conceptual)

### Common Primitives
- `id`: string  
  Opaque unique identifier.

- `timestamp`: string  
  ISO 8601 UTC timestamp.

- `spec_version`: string  
  Authoritative specification identifier (e.g., commit hash or version tag).

- `actor_id`: string  
  Role-qualified actor identifier (human or agent).

- `digest`: string  
  Cryptographic digest over a canonical serialization of the referenced object
  or payload. Digest algorithm selection is implementation-defined but MUST be
  consistent within a deployment.

### Common Invariants
- Every persistent record MUST include `id`, `timestamp`, `spec_version`, and
  `digest` (or an explicit reason field explaining the absence of a digest).
- `id` values MUST be stable and immutable once created.

---

## API / Interface Contracts

Each contract below is defined as a conceptual JSON object schema. Field types
are `string`, `number`, `boolean`, `object`, or `array`. Required fields MUST be
present.

---

### 1) Trend Ingestion

#### Input: `IngestRequest`
Required fields:
- `request_id` (string)
- `source_id` (string)
- `received_at` (timestamp)
- `payload_ref` (object)
- `spec_version` (string)

`payload_ref` (object) required fields:
- `type` (string)
- `uri` (string)
- `digest` (string)
- `size` (number)

**Invariants & Validation Rules**
- `request_id`, `source_id`, `uri`, and `digest` MUST be non-empty.
- `received_at` MUST be less than or equal to processing time and MUST be UTC.

#### Output: `IngestResponse`
- `request_id` (string)
- `ingest_event_id` (string)
- `status` (string: `queued`, `accepted`, `rejected`)
- `reason` (string, REQUIRED if `status` = `rejected`)
- `timestamp` (timestamp)
- `spec_version` (string)

Failure responses MUST conform to `ErrorObject`.

---

### 2) Signal Aggregation

#### Input: `AggregationRequest`
Required fields:
- `request_id` (string)
- `input_event_ids` (array[string], ordered)
- `aggregation_window` (object: `{ start, end }`)
- `spec_version` (string)

#### Output: `AggregationResponse`
Required fields:
- `request_id` (string)
- `aggregation_id` (string)
- `generated_at` (timestamp)
- `trend_candidates` (array[object], ordered)

`trend_candidate` required fields:
- `candidate_id` (string)
- `score` (number)
- `primary_tag` (string)
- `contributing_event_ids` (array[string])
- `provenance_summary` (object)
- `spec_version` (string)

**Invariants & Validation Rules**
- `aggregation_id` and all `candidate_id` values MUST be unique.
- Ordering of `trend_candidates` MUST be deterministic given identical inputs
  and `spec_version`.

---

### 3) Idea Artifact Generation

#### Output: `IdeaArtifact`
Required fields:
- `artifact_id` (string)
- `candidate_id` (string)
- `created_at` (timestamp)
- `created_by` (actor_id)
- `title` (string)
- `description` (string)
- `variants` (array[object], non-empty)
- `metadata` (object)
- `provenance` (array[object], ordered)
- `spec_version` (string)

`variant` required fields:
- `variant_id` (string)
- `text` (string)
- `metadata` (object)

Metadata MUST include:
- `target_platforms` (array[string])
- `estimated_risk_score` (number, range `[0.0, 1.0]`)
- `tags` (array[string])

**Invariants & Validation Rules**
- `artifact_id` MUST be unique and immutable.
- Ordering of `variants` MUST be deterministic and preserved.

On creation, the system MUST emit an `ArtifactCreatedResponse` containing
`artifact_id`, `created_at`, and `spec_version`.

---

### 4) Approval Workflow

#### Input: `ApprovalRequest`
Required fields:
- `approval_request_id` (string)
- `artifact_id` (string)
- `requested_by` (actor_id)
- `requested_at` (timestamp)
- `required_approver_role` (string)
- `policy_reference` (string)
- `spec_version` (string)

Optional:
- `expiry` (timestamp, MUST be > `requested_at` if present)

#### Input: `ApprovalDecision`
Required fields:
- `approval_request_id` (string)
- `decision_id` (string)
- `artifact_id` (string)
- `approver_id` (actor_id)
- `decision` (string: `approve`, `reject`, `modify`, `escalate`)
- `decision_timestamp` (timestamp)
- `justification` (string or object)
- `spec_version` (string)

Justification MUST be present. Policy artifacts MAY require structured
key/value justification and define minimum content rules.

#### Output: `ApprovalOutcome`
- `approval_request_id`
- `decision_id`
- `artifact_id`
- `result_state` (`Approved`, `Rejected`, `Modified`, `Escalated`)
- `decision_timestamp`
- `spec_version`

**Invariants**
- Decisions MUST reference a valid approval request.
- Escalation outcomes MUST record escalation targets.

---

### 5) Externally Observable Actions

#### Input: `ActionCommand`
Required fields:
- `action_id` (string)
- `artifact_id` (string)
- `commanded_by` (actor_id)
- `commanded_at` (timestamp)
- `action_type` (string)
- `target_endpoint` (string)
- `spec_version` (string)

Conditional:
- `approval_reference_id` (string, REQUIRED unless policy explicitly allows auto-action)
- `policy_reference` (string, REQUIRED if approval is not required)

#### Output: `ActionEvent`
Required fields:
- `action_event_id` (string)
- `action_id` (string)
- `artifact_id` (string)
- `actor_id` (actor_id)
- `action_type` (string)
- `target_endpoint` (string)
- `approval_reference_id` (string)
- `status` (`pending`, `executed`, `failed`, `rejected`)
- `timestamp` (timestamp)
- `spec_version` (string)

**Invariants**
- Actions MUST NOT execute without valid authorization.
- All state transitions MUST be recorded as audit events.

---

## Event & Audit Record Schemas (MCP)

### EventRecord (Required Core Fields)
- `event_id` (string)
- `event_type` (string)
- `timestamp` (timestamp)
- `actor_id` (string)
- `spec_version` (string)
- `payload_ref` (object: `{ type, id, digest }`)
- `prev_event_id` (string | null)
- `digest` (string)
- `tamper_evidence` (object)

**Event Store Invariants**
- Events MUST be append-only.
- Ordering MUST be by `timestamp`; ties resolved by `event_id`.
- Implementations MUST NOT rely on wall-clock monotonicity for ordering.

**Query Requirements**
- Events MUST be queryable by `event_type`, `artifact_id`, `actor_id`,
  `spec_version`, and time range.

### Provenance Chain
- All artifacts MUST include an ordered provenance chain referencing event ids
  that materially affected the artifact.

---

## Error & Failure Contracts

### ErrorObject
Required fields:
- `error_id` (string)
- `error_code` (string)
- `message` (string)
- `details` (object | null)
- `timestamp` (timestamp)
- `related_event_id` (string | null)
- `spec_version` (string)

**Failure Semantics**
- Transient failures SHOULD include retry metadata.
- Permanent failures MUST include deterministic reason fields.

---

## Validation & Determinism Rules

- Canonical serialization MUST use UTF-8 encoding, lexicographic object key
  ordering, and no insignificant whitespace.
- All ordered arrays MUST be deterministic and reproducible.
- Resource-creating APIs MUST be idempotent using request identifiers.
- Validation failures MUST return `ErrorObject` with `error_code`
  `VALIDATION_ERROR`.

---

## Security & Access-Control Interfaces (Conceptual)

- `actor_id` MUST map to an authenticated identity and role set.
- Every API call and event MUST record the effective role.
- Authorization failures MUST return `ErrorObject` with `error_code`
  `AUTHZ_FAILURE`.

---

## Spec-Version Binding Requirements

- All artifacts, events, and error responses MUST include `spec_version`.
- Tests and audits MUST be able to reproduce behavior by replaying inputs
  against the recorded `spec_version`.

---

This technical contract document is authoritative for implementation interfaces,
test fixtures, and audit expectations. Any modification MUST be performed via an
approved change to `specs/` and accompanied by updated schema examples and
corresponding test fixtures.