Derived from Spec Kit artifacts: Constitution, Product Spec, Technical Plan, Tasks

spec_version: 0.1

# Security Specification — Project Chimera

Purpose
- Provide an implementable, normative security specification for authentication,
  authorization, secrets management, rate limiting, content moderation, and agent
  containment that aligns with `specs/functional.md` and `specs/technical.md`.

Normative rules (summary)
- All security controls described here are normative. Use of MUST, MUST NOT, SHOULD,
  and MAY are intentional and binding for implementers.
- Secrets MUST NOT be stored in the repository. Secrets in any form (keys, tokens,
  certs) MUST be sourced from platform-managed secrets (e.g., cloud KMS/Secrets Manager).
- All externally observable actions require ledger recording per `LedgerEntry`.

## 1) Authentication (AuthN)

Selected approach: OAuth2 Authorization Code flow with JWT access tokens (Bearer tokens).

Normative details:
- The system MUST accept and validate JWT access tokens signed by the configured
  identity provider (IdP). Token validation MUST include signature verification,
  audience (`aud`), issuer (`iss`), and expiry (`exp`).
- `actor_id` MUST be derived from a claim named `sub` (subject) in the validated JWT.
- Roles MUST be conveyed in a `roles` claim (array of strings) inside the JWT or
  be resolvable via an introspection endpoint. The presence of a `roles` claim is
  REQUIRED for short-lived system tokens; otherwise the UI/backend MUST fetch roles
  from the identity service and cache them for a short TTL (e.g., 5 minutes).
- Refresh tokens and long-lived credentials MUST NOT be used by agents to perform
  externally observable actions; agents must use short-lived access tokens.

Operator vs Service accounts:
- Human users authenticate via OAuth2 Authorization Code flow and receive JWTs with
  `actor_type: "human"` in claims. Service-to-service calls MUST use machine/service
  tokens with `actor_type: "service"` and be scoped to minimal privileges.

## 2) Authorization (AuthZ)

Model: Role-based access control (RBAC) with endpoint-level enforcement.

Roles (normative):
- `operator` — submit ingest requests, view data, generate ideas, schedule (requests only).
- `approver` — review, approve, reject, and enable publish actions.
- `auditor` — read-only access to ledger and audit data.
- `admin` — manage feature toggles, rotation actions, and emergency overrides (requires dual-approval).

Per-endpoint role requirements (normative table)

| Endpoint (HTTP)                       | Minimum Role Required | Action Type           | Notes (ledger event) |
|---------------------------------------|-----------------------|-----------------------|----------------------|
| POST /api/ingest                      | operator              | create/request        | ledger: ingest.requested |
| GET /api/ingest/{id}                  | operator              | read                  | ledger: ingest.read  |
| POST /api/content/generate            | operator              | create                | ledger: idea.generated |
| POST /api/approvals                   | approver              | create/approve        | ledger: approval.created |
| GET /api/approvals?status=pending     | approver              | read                  |                      |
| POST /api/publish                     | approver              | external-action       | ledger: publish.requested |
| POST /api/schedule                    | operator              | create/schedule       | ledger: engagement.scheduled |
| GET /api/ledger                       | auditor               | read (paginated)      |                      |
| POST /api/credentials/rotate          | admin                 | manage                | ledger: credential.rotated |
| POST /api/admin/feature-toggle        | admin (dual-approval) | manage                | ledger: feature.toggle  |

Authorization enforcement:
- All endpoints MUST validate JWT and enforce role membership before processing.
- For critical actions (publish, credential rotation, feature toggle enable), the backend
  MUST require a ledger-backed approval event and, where specified, dual-approval (two distinct
  approvers) for admin overrides.

## 3) Secrets Management

Principles (normative):
- No secrets in repo: secrets MUST NOT be committed to source control in any form.
- Dev vs Prod separation:
  - Development: developers MAY use local secret injection (e.g., `.env` loaded from
    a local secrets manager) with explicit detection and logging when running in dev.
  - Production: secrets MUST be stored in managed secret stores (e.g., AWS Secrets Manager,
    Azure Key Vault) and accessed via short-lived credentials and managed roles.
- Rotation:
  - Secrets MUST have rotation schedules. Credentials used for external publishing MUST
    be rotated at configurable intervals (default 90 days) or on suspicion of compromise.
  - Rotation events MUST produce ledger entries `credential.rotated` with `actor_id`, `timestamp`,
    and `spec_version`.
- Access controls:
  - Microservices MUST assume role-based invocation via platform IAM and obtain secrets at runtime.
  - Local developer tokens MUST be scoped and expire quickly.

## 4) Rate Limits

Global rules (normative):
- Rate limits MUST be enforced at API gateway/edge and at service level.
- Rate limiting responses MUST not leak internal details; errors MUST return an ErrorObject
  pattern per `specs/technical.md` and corresponding ledger entry for throttled critical actions.

Default per-surface limits (examples, configurable):

| API Surface            | Rate Limit (per actor) | Burst | Notes |
|------------------------|------------------------:|------:|-------|
| Ingest (POST /api/ingest) | 60 requests/hour       | 10    | Operators may request frequent ingests but limited to avoid overload |
| Content Generation     | 30 requests/hour        | 5     | Computation-heavy; billed accordingly |
| Publish (POST /api/publish) | 5 requests/day         | 1     | Very strict; requires approval |
| Schedule (POST /api/schedule) | 20 requests/day      | 5     | Scheduling operations constrained |
| Ledger read (GET /api/ledger) | 1000 requests/hour  | 200   | Auditors may query extensively; pagination required |

Throttling policy:
- On hitting limit, gateway returns 429 with ErrorObject and creates ledger entry `throttle.event`.
- Critical publish attempts beyond limits MUST be rejected and create `publish.failed` ledger entries.

## 5) Content Safety & Moderation Pipeline

Overview (normative):
- All candidate content MUST pass a deterministic moderation pipeline before approval or publish.
- The pipeline MUST be deterministic given the same content input and the same spec_version and
  moderation model version. Non-deterministic classifiers MUST be flagged and their seed/parameters
  included in provenance.

Pipeline steps (ordered, each step MUST emit a checkpoint event to ledger):
1. Static policy filter — block by explicit disallowed categories (exact match) (fast, deterministic).
2. PII detector — detect and redact or flag PII; if PII present, route to escalation.
3. Safety classifier — model-based risk scoring (returns risk_score: 0-100) and classification tags.
4. Policy rules engine — deterministic rule evaluation combining risk_score, tags, and policy artifacts.
5. Decision step — mapping of aggregated signals to action:
   - If `risk_score` >= 90 OR policy engine returns `block`, outcome MUST be `BLOCK`.
   - If 60 <= `risk_score` < 90 OR some policy flags, outcome MUST be `REVIEW`.
   - If `risk_score` < 60 and no rule flags, outcome MUST be `ALLOW`.
6. Escalation: `REVIEW` or `BLOCK` outcomes MUST create ledger events and assign to Approver queue.

Deterministic outcomes and explainability:
- Each decision MUST include `decision_id`, `decision_reason` (structured), `model_version`, and
  `spec_version` in the recorded event.

Escalation rules:
- `BLOCK` outcomes: do NOT allow publication; notify security and record `content.blocked` ledger event.
- `REVIEW` outcomes: place item in Approval Inbox and create `content.review` ledger event.
- Approver overrides (approve after REVIEW) MUST include explicit justification and produce `approval.override`
  ledger events with `actor_id` and `justification`.

## 6) Agent Containment & Network Policy

Forbidden actions (normative):
- Agents and runtime skills MUST NOT directly exfiltrate data to arbitrary external endpoints.
- Agents MUST NOT perform writes to external social platforms without a verified ledger `approval_id` and
  a matching publish ledger entry.

Network allowlist policy:
- Each runtime environment MUST enforce outbound allowlists. At minimum, allowlisted destinations include:
  - Approved content storage endpoints (CDN/object store) with documented `payload_ref` schema.
  - Approved telemetry/analytics endpoints (Tenx MCP Sense proxy) as configured.
  - Identity provider and vault endpoints for auth and secrets.
- All other outbound connections MUST be denied by default.

Resource limits (normative):
- Each agent execution MUST run within constrained compute limits: CPU (e.g., 1 vCPU), memory (e.g., 2 GB),
  and wall-time (e.g., 5 minutes) unless explicitly annotated in the spec and approved by admin.
- Long-running or high-memory tasks MUST be scheduled to controlled worker pools and MUST record resource usage
  metrics to telemetry and ledger if they trigger thresholds.

Human escalation triggers (examples):
- Multiple `BLOCK` decisions for similar content within short time window (configurable) MUST trigger security alert.
- Credential failures (401/403) for publishing endpoints MUST trigger immediate `credential.failed` ledger events and
  pause publishing for affected actors.

## 7) Audit Mapping (security events -> LedgerEntry)

All security-relevant events MUST be recorded as `LedgerEntry` objects per `specs/technical.md`. Minimum mapping:

| Security Event                      | LedgerEntry.action        | Required fields (subset) |
|-------------------------------------|---------------------------|--------------------------|
| auth.success                        | auth.success              | event_id,timestamp,actor_id,spec_version,metadata(auth_method) |
| auth.failure                        | auth.failure              | event_id,timestamp,actor_id?,spec_version,details(error)     |
| ingest.requested                    | ingest.requested          | event_id,timestamp,actor_id,request_id,spec_version,payload_digest |
| idea.generated                      | idea.generated            | event_id,timestamp,actor_id,ingest_event_id,spec_version      |
| approval.created                    | approval.created          | event_id,timestamp,actor_id,approval_id,approved_spec_version |
| publish.requested                   | publish.requested         | event_id,timestamp,actor_id,publish_request_id,approval_id,spec_version,payload_digest |
| publish.executed                    | publish.executed          | event_id,timestamp,actor_id,publish_request_id,external_response_digest,spec_version |
| publish.failed                      | publish.failed            | event_id,timestamp,actor_id,publish_request_id,error_id,spec_version |
| throttle.event                      | throttle.event            | event_id,timestamp,actor_id,rate_limit,scope,spec_version     |
| credential.rotated                  | credential.rotated        | event_id,timestamp,actor_id,credential_id,spec_version        |
| content.decision (ALLOW/REVIEW/BLOCK)| content.decision         | event_id,timestamp,actor_id,content_id,decision,decision_reason,model_version,spec_version |

Ledger recording rules (normative):
- Each mapping MUST include `spec_version`, `actor_id` (or service id), and `payload_digest` where applicable.
- Ledger entries MUST be created before the corresponding external action completes.

Compliance & Forensics
- Ledger exports for forensics MUST include chained `prev_event_id` to reconstruct causal order and payload digests for verification.

---

This file defines the required security posture for Project Chimera and is intended to be
consumed by implementers and automated agents responsible for producing secure runtime code.
