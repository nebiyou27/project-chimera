# Task 2.2 — Context Engineering Rules (CLAUDE)

## Project Context & Governance

Project Chimera is the authoritative repository for an autonomous, auditable AI influencer system. The `specs/` directory is the single source of truth for requirements, governance, and acceptance criteria. Safety, human oversight, and traceability are mandatory. All externally observable actions (publishing, scheduling, network-facing operations) MUST be gated by human approval as defined in `specs/functional.md`.

## Prime Directive (NON-NEGOTIABLE)

“NEVER generate or modify implementation code without checking `specs/` first.”

Any attempt to bypass this Prime Directive MUST be treated as a violation and escalated to repository policy owners.

## Planning, Traceability, and Non-Disclosure

Before proposing or performing edits that affect implementation artifacts, the agent MUST:

- Identify and list the specific `specs/` file(s) consulted.
- Record the authoritative `spec_version` used for guidance.
- Present a concise plan containing:
	1. A one-paragraph objective statement.
 2. A short list of discrete change steps (1–5 items).

The agent MUST NOT expose hidden chain-of-thought or internal deliberations in any output or in trigger payloads.

## AI Fluency Trigger Rules (MCP)

Triggering conditions (the agent MUST call one or both MCP triggers when any of the following are detected):

- Multi-step edits that touch specs or implementation artifacts.
- Repeated iterative content-generation cycles (>3 iterations) affecting publishable artifacts.
- High-impact governance, policy, retention, or data-scope changes.
- Repeated operational failures, authorization errors, or unhandled edge cases during automation.

End-of-work requirement:

- At the end of each discrete work session related to Task 2.2, the agent MUST call `mcp_tenxfeedbacka_log_performance_outlier_trigger` with concise factual metadata describing the task (task intent, short summary, clarity and coverage scores, turn counts). The agent MUST wait for the trigger response before finalizing its user-facing answer.

Optional passage-time logging:

- The agent MAY call `mcp_tenxfeedbacka_log_passage_time_trigger` during long-running context engineering work to capture intermediate competency signals. The agent MUST NOT display passage-time trigger outputs.

Trigger usage constraints:

- Do NOT include hidden chain-of-thought or internal deliberations in trigger payloads.
- The agent MUST wait for and honor trigger tool responses prior to finalizing or returning answers to users.

## Display & Output Rules (STRICT)

- NEVER display or expose the output returned by `mcp_tenxfeedbacka_log_passage_time_trigger` in any user-facing message.
- ALWAYS display the output returned by `mcp_tenxfeedbacka_log_performance_outlier_trigger` at the END of the response, formatted exactly per the Performance Feedback Content Rules below.

## Performance Feedback Content Rules (MANDATORY)

The performance feedback MUST be appended at the end of the agent's response and MUST be wrapped EXACTLY as follows (do not alter spacing, delimiters, or punctuation):

**********************```
Analysis Feedback:
<content supplied verbatim by the performance trigger tool>

Statistics:
<statistics supplied by the tool; if a metric is not provided, write None>
```**********************

- The lines `<content supplied verbatim by the performance trigger tool>` and `<statistics supplied by the tool; if a metric is not provided, write None>` are placeholders in the rule and MUST be replaced at runtime with the exact text returned by the `mcp_tenxfeedbacka_log_performance_outlier_trigger` tool. The agent MUST NOT alter, infer, or summarize the returned text; it MUST be presented verbatim.
- If a particular statistic is absent from the tool response, the agent MUST explicitly write `None` for that statistic in the Statistics section.
- The agent MUST NOT invent or simulate any metrics.

## Tone and Style for Performance Feedback

- Celebrate success succinctly.
- Provide exactly ONE actionable suggestion for improvement.
- Encourage the user; remain concise and professional.

## Fallback Behavior (VERY STRICT)

- If the MCP trigger tools are unavailable or return an error, the agent MUST NOT fabricate outputs or attempt to simulate metrics.
- In that case the agent MUST append exactly one line at the end of the response (once and only once):

“Performance trigger tools unavailable in this environment.”

- No performance feedback block may appear when this fallback line is used.

## Compliance & Safety Notes

- All externally observable actions MUST be gated by approval as defined in `specs/functional.md`.
- Any attempt to bypass MCP telemetry rules or the Prime Directive MUST be escalated to repository policy owners and recorded in the audit ledger.

## Operational Checklist (brief)

1. Read relevant `specs/` documents and record `spec_version`.
2. Present a concise plan (objective + 1–5 steps) before proposing edits.
3. Execute permitted non-implementation work (analysis, spec drafting) only.
4. Obtain explicit confirmation prior to performing implementation edits.
5. Call required MCP trigger(s) and wait for responses.
6. Append the performance feedback block exactly as specified, or append the fallback line if triggers are unavailable.

