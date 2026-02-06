Derived from Spec Kit artifacts: Constitution, Product Spec, Technical Plan, Tasks

spec_version: 0.1

# Frontend Specification — Project Chimera

Purpose
- This document defines the UI surface, roles, flows, wireframes, component hierarchy,
  and API mappings required for a production-ready frontend that operates against the
  contracts and ledger defined in `specs/technical.md`.
- This is a specification-only artifact. No implementation code is included.

Normative constraints
- All externally visible UI actions that cause state change MUST be gated by HITL
  approvals where the underlying contract or spec requires it.
- Every UI action that initiates an externally observable change MUST attach `spec_version`
  and `actor_id` and record the resulting ledger event per `LedgerEntry` in `specs/technical.md`.

1) Roles & Permissions
- Operator
  - Can view Trend Queue, Idea Review, Approval Inbox, and Audit Explorer.
  - Can request runs (ingest/aggregate) and queue items for ideation.
  - Can create requests that require Approver action. Their actions MUST be recorded with `actor_id`.
  - Cannot approve publish actions.
- Approver
  - Can review, approve, or reject publishable content items.
  - Can create HITL approvals recorded as LedgerEntry with `approval_id` and `approved_spec_version`.
  - Can enable/disable publishing feature toggles (UI control) when policy allows.
- Auditor
  - Read-only access to Audit Explorer and immutable ledger views.
  - Can export ledger slices for compliance review.

Permission mapping (normative):
- `Operator` MAY perform `ingest.request`, `idea.generate`, `engagement.schedule` (requests only).
- `Approver` MUST perform `approval.create` and MAY perform `publish.execute` after approval.
- `Auditor` MUST NOT perform write actions.

2) Key User Flows (step-by-step)

- Flow A: Submit Trend Ingest Request (Operator)
  1. Operator opens Trend Queue page.
 2. Operator clicks "New Ingest" and fills `source_id`, `since`, `until`, `max_items`.
 3. UI validates input against `TrendFetcherInput` schema from `specs/technical.md`.
 4. UI POSTs to backend ingest endpoint (mapped to TrendFetcherInput).
 5. Backend returns a request acknowledgment; UI displays `request_id` and queued state.
 6. A ledger event `ingest.requested` MUST be created with `actor_id` and `spec_version`.

- Flow B: Review Generated Ideas (Operator -> Approver)
  1. Operator navigates to Idea Review and selects a trend-derived item.
 2. Operator clicks "Generate Ideas"; UI calls ContentGenerator contract endpoint.
 3. Generated ideas are displayed with provenance and risk score.
 4. Operator may mark items for approval; these items move to Approval Inbox.
 5. A ledger event `idea.generated` MUST be recorded referencing `ingest_event_id`.

- Flow C: Approval & Publish (Approver)
  1. Approver opens Approval Inbox.
 2. Approver inspects item metadata, payload_ref, provenance, and risk score.
 3. Approver clicks "Approve" and adds justification; UI assembles an `approval` object.
 4. UI submits approval; backend writes a LedgerEntry `approval.created` with `approval_id`.
 5. Approver may then trigger `publish` action; the orchestrator validates the approval_id
     against ledger before performing external call. Publish attempts MUST create `publish.requested`
     then `publish.executed` or `publish.failed` ledger entries.

- Flow D: Schedule Engagement (Operator)
  1. Operator selects approved content and opens scheduling modal.
  2. Operator sets `scheduled_at` and audience parameters.
  3. UI validates against EngagementManagerInput contract and submits schedule request.
  4. Backend writes an `engagement.scheduled` ledger event and returns `engagement_id`.

- Flow E: Audit Investigation (Auditor)
  1. Auditor opens Audit Explorer and queries by `event_id`, `actor_id`, or `spec_version`.
  2. UI calls audit query API (maps to LedgerEntry read endpoints) and displays entries.
  3. Auditor can expand entries to view payload digests, prev_event_id chains, and exports a snapshot.

3) Wireframes (ASCII)

- Trend Queue (columns: queued, processing, failed)

  +-------------------------------------------------------------+
  | Trend Queue                                                 |
  | [New Ingest] [Filter by source] [Spec Version]              |
  +-------------------------------------------------------------+
  | Queued                | Processing             | Failed       |
  | --------------------- | ---------------------- | ------------ |
  | [request_id] source   | [request_id] source    | [request_id] |
  | - items: 12           | - started_at           | - error_code  |
  +-------------------------------------------------------------+

- Idea Review

  +-------------------------------- Idea Review --------------------------------+
  | [Trend item header]  [provenance]  [risk-score]  [Generate Ideas] [Export]  |
  +------------------------------------------------------------------------------+
  | Idea list (cards)                                                             |
  | [Idea card] title | preview | payload_ref | provenance | [Mark for Approval]  |
  +------------------------------------------------------------------------------+

- Approval Inbox

  +----------------------------- Approval Inbox -------------------------------+
  | [Filter: pending/approved/rejected] [Spec Version] [Search approvals]      |
  +----------------------------------------------------------------------------+
  | [approval_id] content_id | actor | requested_at | status | [View] [Approve]  |
  +----------------------------------------------------------------------------+

- Audit Explorer

  +----------------------------- Audit Explorer -------------------------------+
  | [Query bar: event_id|actor_id|spec_version] [Date range] [Export]         |
  +----------------------------------------------------------------------------+
  | Ledger entries (paginated)                                                 |
  | [event_id] [timestamp] [actor_id] [action] [resource_id] [spec_version]    |
  +----------------------------------------------------------------------------+

4) Component Hierarchy
- AppShell
  - Header (role switcher, actor display, spec_version badge)
  - Nav (Trend Queue, Idea Review, Approval Inbox, Audit Explorer, Settings)
  - Main Router
    - TrendQueuePage
      - IngestForm (validates TrendFetcherInput)
      - QueueTable (rows -> QueueRow component)
    - IdeaReviewPage
      - TrendItemHeader
      - IdeaCardList (IdeaCard)
      - GenerateModal
    - ApprovalInboxPage
      - ApprovalList (ApprovalRow)
      - ApprovalDetailModal
    - AuditExplorerPage
      - AuditQueryForm
      - LedgerTable (LedgerRow, ExpandableDetail)
    - SettingsPage
      - FeatureToggles (publishing_enabled)
      - CredentialStatus (read-only prompts to integrators)

5) API Mapping Table (UI action -> contract / section in `specs/technical.md`)

- "New Ingest" (UI) -> `TrendFetcherInput` / `TrendFetcherOutput` (specs/technical.md: TrendFetcher Input/Output)
- "Generate Ideas" -> `ContentGeneratorInput` / `ContentGeneratorOutput` (specs/technical.md: ContentGenerator Input/Output)
- "Approve" -> LedgerEntry `approval` pattern (specs/technical.md: LedgerEntry + Approval workflow in openclaw_integration.md)
- "Publish" -> `OpenClawPublishRequest` (specs/openclaw_integration.md: PublishRequest)
- "Schedule Engagement" -> `EngagementManagerInput` / `EngagementManagerOutput` (specs/technical.md: Engagement Manager)
- "Audit Query" -> `LedgerEntry` read endpoints (specs/technical.md: LedgerEntry)

6) Non-functional UI Requirements
- Accessibility: UI MUST conform to WCAG 2.1 AA where applicable (semantic HTML, keyboard navigation, ARIA labels).
- Loading states: All async actions MUST display skeletons or spinners and disable destructive controls while pending.
- Error states: Validation errors MUST be surfaced inline; server errors MUST display a non-sensitive error card and create an `ErrorObject` ledger entry.
- Audit visibility: Every action that writes ledger entries MUST show a confirmation with `event_id` and link to the Audit Explorer.
- Performance: List pages MUST be paginated; default page size MUST be ≤ 50 to avoid heavy loads.
- Security: UI MUST never display credentials; any hints about secrets MUST be obfuscated and direct users to secure credential stores.

Appendix: UI → Ledger Expectations (normative)
- Any UI-initiated externally observable action MUST record a LedgerEntry BEFORE the action completes and show the `event_id` to the user.
