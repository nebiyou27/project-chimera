# Project Chimera — Functional Specification

## Overview
This document enumerates agent-oriented functional capabilities for Project Chimera.
Each capability is expressed as one or more user stories of the form
“As an Agent, I need…” followed by precise, deterministic acceptance criteria.
The focus is WHAT the system must provide; implementation techniques are
intentionally omitted.

---

## Terminology
- **Artifact:** Any generated object subject to lifecycle management
  (e.g., trend candidate, idea, content draft).
- **Event Ledger:** An append-only, tamper-evident log of system actions and decisions.
- **Externally Observable Action:** Any action that produces effects outside
  Project Chimera’s internal boundary, including publication, scheduling,
  notification, or third-party API side effects.

---

## Capability Sections (contents)
- Trend discovery and ingestion
- Signal aggregation & ranking
- Idea generation and candidate packaging
- Candidate lifecycle and metadata
- Human-in-the-loop review & approval (HITL)
- Publishing and external action gating
- Policy, risk classification, and escalation
- Observability, provenance, and auditability (MCP)
- Data handling, retention, and access controls
- Acceptance, test, and compliance requirements

---

## 1. Trend Discovery and Ingestion

### User Stories
- As an Agent (TrendCollector), I need to gather public signals from configured
  social and public data endpoints so that potential trends are captured for
  downstream analysis.

### Acceptance Criteria
- Given a configured collection period and source list, the system produces a
  time-stamped event batch containing source identifier, fetch timestamp (UTC),
  and a raw payload reference.
- Each ingestion event must be recorded with a unique identifier and persisted
  to a tamper-evident event ledger accessible to observability queries.
- **Duplicate suppression:** events with identical canonical source identifiers
  and identical payload digests within the same collection period must be
  deduplicated; the deduplication outcome must be recorded.
- **Failure semantics:** when an ingestion attempt fails for a source, the system
  records a failure event with error class and retry metadata; failures do not
  cause loss of prior successful events.

### HITL Points
- None required for ingestion; ingestion metadata is available for human review
  and audit.

---

## 2. Signal Aggregation & Ranking

### User Stories
- As an Agent (SignalAggregator), I need to combine ingested signals into ranked
  trend candidates so human reviewers receive prioritized, actionable items.

### Acceptance Criteria
- For a given ingestion window, the system outputs a deterministic ranked list of
  trend candidates including candidate id, score, contributing sources, and
  calculation timestamp (UTC).
- **Determinism:** given identical input event batches and the same spec version,
  the system must produce identical ordered candidate lists.
- Aggregation must attach a provenance summary enumerating contributing events
  and aggregation window bounds.

### HITL Points
- Review of ranked trend candidates is optional prior to idea generation; any
  externally observable action derived from a candidate must later pass approval.

---

## 3. Idea Generation and Candidate Packaging

### User Stories
- As an Agent (IdeaGenerator), I need to produce structured content-idea artifacts
  for each trend candidate that include creative variants and metadata for human
  review.

### Acceptance Criteria
- Each idea artifact must include: unique artifact id, linked trend candidate id,
  timestamps, textual description, structured metadata (tags, target platforms,
  estimated risk class), and an explicit provenance record linking back to
  contributing events and the authoritative spec version.
- For each candidate, the system must produce at least **N** distinct idea
  variants, where **N** is a configurable, recorded parameter included in the
  artifact metadata.
- All generated artifacts must be stored in a candidate repository and indexed
  for retrieval by id, risk class, and timestamp.

### HITL Points
- Human review is required before any idea artifact is promoted to a publishable
  action. Promotion attempts must be recorded and routed to the approval workflow.

---

## 4. Candidate Lifecycle and Metadata

### User Stories
- As an Agent (CandidateManager), I need to store, version, annotate, and
  transition candidate artifacts through lifecycle states so workflows and
  audits can track status and lineage.

### Acceptance Criteria
- Candidate artifacts must support explicit lifecycle states
  (e.g., Draft, Submitted, Approved, Rejected, Promoted, Published, Archived).
- All lifecycle transitions must be recorded as immutable state-change events
  containing actor id, timestamp, from-state, to-state, and justification.
- **Versioning:** any mutation produces a new version with an incrementing
  version identifier; prior versions remain retrievable by id and version.
- **Annotation:** actors (human or agent) may attach structured key/value
  annotations; each annotation is recorded with actor id and timestamp.

### HITL Points
- Submission for approval and final approval are explicit HITL actions.
  Any transition to `Published` requires a recorded approval unless policy
  explicitly authorizes auto-publication.

---

## 5. Human-in-the-Loop Review & Approval

### User Stories
- As an Agent (WorkflowCoordinator), I need to present candidate artifacts and
  required context to human Approvers, collect decisions, and record outcomes so
  externally observable actions are explicitly authorized.

### Acceptance Criteria
- **Presentation bundle:** the system produces a review bundle containing
  candidate artifacts, provenance records, risk classification, and change
  history sufficient for informed approval.
- **Approval recording:** an approval decision must be recorded as an approval
  event containing approver id, decision
  (approve / reject / modify / escalate), UTC timestamp, and mandatory
  justification expressed as structured text or key/value metadata.
- **Timeboxing:** approval requests must include expiry metadata; expired
  requests revert artifacts to a configurable default state (e.g., Draft) and
  record an expiry event.
- **Decision determinism:** given identical input bundles and approver decisions,
  resulting state transitions and events must be identical and queryable.

### HITL Points (Explicit)
- Approval is required for any externally observable action unless an explicit
  policy artifact authorizes otherwise. Approval must be provided by a role
  defined in `specs/` and recorded in the event ledger.

---

## 6. Publishing and External Action Gating

### User Stories
- As an Agent (Publisher), I need to execute externally observable actions only
  after required approvals are recorded and emit action events for audit.

### Acceptance Criteria
- **Gate enforcement:** attempts to perform externally observable actions without
  a valid approval event must be rejected and logged as authorization failures.
- **Action event:** successful actions produce an event including action id,
  actor id, target endpoint identifier, affected artifact ids, approval
  reference id, UTC timestamp, and outcome status.
- **Rate and scope enforcement:** actions violating active rate limits or scope
  constraints must be rejected with recorded reasons.

### HITL Points
- Final publish actions require recorded approval. Scheduling may occur only as
  a pending action that cannot execute until approval is present.

---

## 7. Policy, Risk Classification, and Escalation

### User Stories
- As an Agent (PolicyEvaluator), I need to classify artifacts by risk and apply
  policy rules to determine approval levels and escalation paths.

### Acceptance Criteria
- **Risk tagging:** each artifact must include a risk class and numeric risk
  score referencing the policy artifact version used.
- **Approval mapping:** policy artifacts deterministically map risk classes to
  required approver roles and checks; the applied mapping is recorded.
- **Escalation:** rejected or escalated artifacts generate escalation events and
  are routed to higher-privilege roles as defined by policy; routing decisions
  are recorded.

### HITL Points
- Escalation routes decisions to higher-privilege human approvers; all escalation
  events are auditable.

---

## 8. Observability, Provenance, and Auditability (MCP)

### User Stories
- As an Agent (Auditor), I need to query event sequences, provenance chains, and
  artifact histories so every externally observable decision is reproducible and
  auditable.

### Acceptance Criteria
- **Event completeness:** all significant events (ingestion, aggregation,
  generation, versioning, submission, approval, publish, failure) are present in
  the event ledger and searchable by time range, artifact id, and actor id.
- **Provenance chains:** for any artifact id, the system provides a complete
  provenance chain including source events, processing steps, generator ids,
  authoritative spec version, and timestamps.
- **Spec-version binding:** every event and artifact includes the authoritative
  spec identifier active at the time of the event.

### HITL Points
- Auditors may request read-only reproduction bundles for review; such requests
  do not alter artifact state.

---

## 9. Data Handling, Retention, and Access Controls

### User Stories
- As an Agent (DataController), I need to enforce data minimization, retention
  schedules, and role-based access so privacy and policy constraints are met.

### Acceptance Criteria
- **Retention schedules:** each data class is associated with a retention policy;
  deletion or archival events record the triggering policy id and timestamp.
- **Access controls:** access to sensitive data or re-identification capabilities
  is restricted to specified roles and logged with actor id and purpose.
- **Pseudonymization:** where required, raw identifiers are stored as
  pseudonymized references; re-identification access is controlled and auditable.

### HITL Points
- Requests to access re-identification mappings require explicit approval by the
  designated role and are recorded as approval events.

---

## 10. Acceptance, Test, and Compliance Requirements

### User Stories
- As an Agent (ComplianceTester), I need deterministic acceptance tests that
  validate spec conformance so implementations can be verified against the spec.

### Acceptance Criteria
- **Test fixtures:** for each capability, the spec defines at least one
  deterministic fixture with input events, expected outputs, and expected audit
  events.
- **Reproducibility:** executing a capability with identical fixture inputs and
  the same spec version produces identical artifacts and event sequences.
- **Compliance reporting:** on request, the system produces a compliance evidence
  bundle containing representative artifacts, provenance, approval records, and
  spec-version references for a specified time window.

### HITL Points
- Major releases or policy changes require human sign-off recorded in
  change-management events prior to becoming effective.

---

## Notes and Constraints
- All externally observable actions are blocked unless accompanied by a recorded,
  valid approval event, except when explicitly authorized by a versioned policy
  artifact in `specs/policies/`.
- This specification defines WHAT must be delivered; implementation choices are
  left to implementers, who must demonstrate compliance via reproducible tests.

---

## Executable Acceptance Scenarios (Gherkin)
Derived from Spec Kit artifacts: Constitution, Product Spec, Technical Plan, Tasks

### 1) Trend ingestion dedupe + failure logging
Feature: Trend ingestion deduplication and failure recording
  Scenario: Happy path - ingest unique events
    Given a configured source with two non-duplicate payloads within window
    When the ingest is executed for that window
    Then the ledger MUST contain an `ingest.requested` and `ingest.executed` event
    And the output batch MUST contain both payloads with distinct payload digests

  Scenario: Edge case - duplicate payloads in same window
    Given two events with identical canonical source id and identical payload digest
    When the ingest is executed for that window
    Then the system MUST emit a single canonical event for that payload
    And the ledger MUST record a deduplication event referencing the suppressed payload id

  Scenario: Failure mode - source unreachable
    Given a source that returns network error on fetch
    When the ingest attempt is performed
    Then the system MUST emit an `ingest.failed` ledger entry with ErrorObject
    And retries MUST be recorded in ledger with backoff metadata until retry budget exhausted

### 2) Deterministic ranking for same inputs/spec_version
Feature: Signal aggregation determinism
  Scenario: Happy path - identical inputs produce identical ranking
    Given identical ingestion event batch A and spec_version V
    When aggregation runs twice with the same code and config
    Then both runs MUST produce the same ordered candidate list and same scores

  Scenario: Edge case - non-deterministic source flagged
    Given a source marked non-deterministic in metadata
    When aggregation runs
    Then outputs MUST include `metadata.non_deterministic: true` and include seed values

  Scenario: Failure mode - missing spec_version
    Given inputs lacking spec_version
    When aggregation is invoked
    Then the service MUST return an ErrorObject and ledger `error` entry; processing MUST stop

### 3) Approval workflow expiry + justification rules
Feature: Approval expiry and justification enforcement
  Scenario: Happy path - approver provides justification within expiry
    Given an approval request with expiry set to T+24h
    And approver approves with structured justification
    When approval is recorded
    Then a ledger `approval.created` event MUST be written with justification fields

  Scenario: Edge case - approval expired
    Given an approval request past expiry
    When an approver attempts to approve
    Then the system MUST reject the approval and revert artifact to `Draft`
    And ledger MUST contain `approval.expired` event

  Scenario: Failure mode - missing justification
    Given an approver submits approval without justification when policy requires it
    When approval is submitted
    Then the system MUST reject submission with ErrorObject and create ledger `approval.rejected`

### 4) Publishing gating (reject without valid approval_reference_id)
Feature: Publish gating by approval reference
  Scenario: Happy path - publish with valid approval
    Given an approval_id that exists in ledger and matches artifact and spec_version
    When publish is requested with that approval_id
    Then orchestrator MUST perform external publish and create `publish.executed` ledger entry

  Scenario: Edge case - approval_id mismatch
    Given an approval_id that exists but references a different artifact
    When publish is requested with that approval_id
    Then publish MUST be rejected and `publish.failed` ledger entry created with reason `approval_mismatch`

  Scenario: Failure mode - missing approval_id
    Given a publish request lacking approval_id
    When publish is requested
    Then the system MUST reject with ErrorObject and record `publish.rejected` in ledger

### 5) Audit / provenance query completeness
Feature: Audit and provenance completeness
  Scenario: Happy path - full provenance returned
    Given an artifact id with complete history
    When auditor queries provenance by artifact id
    Then the system MUST return a chain of events from ingestion to current state
    And each event MUST include spec_version, actor_id, timestamp, and payload_digest

  Scenario: Edge case - partial retention window
    Given older events beyond retention policy removed
    When auditor queries full provenance
    Then system MUST return available events and a `provenance.incomplete` flag with retention policy id

  Scenario: Failure mode - ledger read failure
    Given the ledger service unavailable
    When an audit query is performed
    Then the system MUST return ErrorObject and create `audit.query.failed` ledger entry

### Non-functional requirements (additions)
- NFR-1 Response time: Aggregation and ranking API endpoints MUST return within 2 seconds (p95) for input batches ≤ 500 items under normal load.
- NFR-2 Queue handling: Trend Queue MUST handle max queue depth of 10,000 pending requests; when queue depth exceeds 8,000, system MUST emit `queue.high_watermark` ledger events and apply backpressure to new ingest requests.
