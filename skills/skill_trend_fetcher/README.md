# Skill: skill_trend_fetcher

Purpose
- The `skill_trend_fetcher` skill is responsible for retrieving, normalizing, and packaging trend signals from configured data sources for downstream processing. It MUST NOT publish or otherwise cause externally observable actions.

It does NOT:
- Perform content generation, approval, or publishing.

Input Contract (JSON)
```json
{
	"request_id": "string",            // idempotency token (MUST)
	"source_id": "string",             // canonical source identifier (MUST)
	"fetch_parameters": {                // configuration for fetch (MUST)
		"since": "string (timestamp)",
		"until": "string (timestamp)",
		"max_items": "number"
	},
	"actor_id": "string",              // requester identity (MUST)
	"spec_version": "string"           // authoritative spec snapshot (MUST)
}
```

Output Contract (JSON)
```json
{
	"ingest_event_id": "string",       // unique id for ingest event (MUST)
	"request_id": "string",            // echoes input request_id (MUST)
	"source_id": "string",
	"fetched_at": "string (timestamp)",
	"items": [                           // array of normalized signal objects (MUST)
		{
			"item_id": "string",
			"payload_ref": { "uri": "string", "digest": "string", "size": "number" },
			"canonical_id": "string",
			"timestamp": "string (timestamp)",
			"metadata": { "tags": ["string"] }
		}
	],
	"provenance": ["string"],          // event ids or source refs (MUST)
	"spec_version": "string"
}
```

Determinism & Invariants
- Given identical `request_id`, `source_id`, `fetch_parameters`, and `spec_version`, the skill SHOULD return the same `items` ordering and content. The `ingest_event_id` MUST be stable for idempotent requests.
- `items[].payload_ref.digest` MUST be present and stable.

Error Handling
- Errors MUST be returned as `ErrorObject` as defined in `specs/technical.md`.
- Common error codes include: `VALIDATION_ERROR`, `FETCH_ERROR`, `AUTHZ_FAILURE`.

Audit & MCP
- The skill MUST emit or return `provenance` references and `ingest_event_id` suitable for MCP event recording. All outputs MUST include `spec_version`.
# skill_trend_fetcher
