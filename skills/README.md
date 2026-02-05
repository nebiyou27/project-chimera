# Skills Registry

This directory contains runtime skill contracts for Project Chimera. Each skill is a self-contained capability package exposing a deterministic Input/Output contract. Implementations MUST follow the contracts in these READMEs and MUST include `spec_version` on all artifacts.

Skills included:

- `skill_trend_fetcher` — Responsible for deterministic retrieval and packaging of trend signals.
- `skill_content_generator` — Responsible for producing idea artifacts and variants for human review.
- `skill_engagement_manager` — Responsible for proposing engagement actions; all externally observable actions MUST be approved and executed outside the skill.

General rules for all skills:

- All inputs and outputs MUST include `spec_version` and `request_id` (when applicable for idempotency).
- Skills MUST be idempotent for repeated requests bearing the same `request_id`.
- Skills MUST produce auditable, machine-readable outputs and MUST emit references to provenance and event ids for MCP audit.
- Skills MUST NOT perform externally observable actions (publish, network calls with side effects); they MAY propose actions which require explicit approval and execution by the approved publisher component.
- Error responses MUST follow the shared `ErrorObject` contract defined in `specs/technical.md`.
# Skills Catalog

This file documents critical Skills available to Chimera agents and their Input/Output contracts. A Skill is a versioned capability package that exposes a small, well-defined interface.

## skill_trend_fetcher
- Purpose: Discover and rank trending topics from configured sources.
- Input:
```json
{
  "request_id": "uuid",
  "sources": ["youtube","twitter","tiktok"],
  "filters": {"language":"en","region":"US"},
  "max_results": 50
}
```
- Output:
```json
{
  "request_id":"uuid",
  "trends": [
    {"id":"tr_123","title":"AI art tools","score":0.92,"source":"twitter"}
  ]
}
```

## skill_download_youtube
- Purpose: Download video assets for processing and store them in object storage.
- Input:
```json
{
  "request_id":"uuid",
  "video_url":"https://www.youtube.com/watch?v=...",
  "target_bucket":"s3://project-chimera-artifacts"
}
```
- Output:
```json
{
  "request_id":"uuid",
  "artifact_url":"s3://project-chimera-artifacts/path.mp4",
  "duration_seconds": 32
}
```

## skill_transcribe_audio
- Purpose: Produce a time-aligned transcript from an audio/video artifact.
- Input:
```json
{
  "request_id":"uuid",
  "artifact_url":"s3://.../file.mp4",
  "language":"en"
}
```
- Output:
```json
{
  "request_id":"uuid",
  "transcript":"...",
  "segments":[{"start":0.0,"end":2.3,"text":"..."}]
}
```

## How to add a Skill
- Create a folder `skills/skill_<name>/` with `contract.json` and `README.md`.
- Include examples and a test file in `tests/` that validates the contract.
