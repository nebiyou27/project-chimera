# Skill: skill_content_generator

Purpose
- The `skill_content_generator` skill is responsible for producing structured idea artifacts and creative variants based on trend candidates. It MUST NOT publish content or perform externally observable actions.

It does NOT:
- Approve, schedule, or publish content.

Input Contract (JSON)
```json
{
  "request_id": "string",          // idempotency token (MUST)
  "candidate_id": "string",        // linked trend candidate id (MUST)
  "input_provenance": ["string"],  // provenance event ids (MUST)
  "parameters": {                     // generation parameters (MUST)
    "variant_count": "number",
    "target_platforms": ["string"]
  },
  "actor_id": "string",
  "spec_version": "string"
}
```

Output Contract (JSON)
```json
{
  "artifact_id": "string",         // unique artifact id (MUST)
  "request_id": "string",          // echoes input request_id (MUST)
  "candidate_id": "string",
  "created_at": "string (timestamp)",
  "created_by": "string",
  "title": "string",
  "description": "string",
  "variants": [                       // at least one variant (MUST)
    {
      "variant_id": "string",
      "text": "string",
      "metadata": { "tags": ["string"], "estimated_risk_score": "number" }
    }
  ],
  "provenance": ["string"],        // chain of event ids (MUST)
  "spec_version": "string"
}
```

Determinism & Invariants
- For identical `request_id`, `candidate_id`, `input_provenance`, and `spec_version`, the skill SHOULD produce identical `variants` ordering and content.
- `variants[].metadata.estimated_risk_score` MUST be within [0.0,1.0].

Error Handling
- Errors MUST conform to `ErrorObject` from `specs/technical.md`.
- Common error codes: `VALIDATION_ERROR`, `GENERATION_ERROR`, `PROVENANCE_MISSING`.

Audit & MCP
- Outputs MUST include `provenance` referencing contributing event ids and the `spec_version` used. The skill MUST return machine-readable artifact metadata suitable for audit logging.
# skill_content_generator
