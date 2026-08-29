# Metrics Framework

AI engineering programs fail in two opposite ways: **no measurement** (anecdote-driven) and **vanity measurement** (activity mistaken for value).

## Metric domains

### Velocity

- Tasks completed / completion rate
- Simulated PR cycle time
- AI-assisted duration vs. estimated manual duration (**labeled estimates**)

### Quality

- Test pass rate
- Reviewer change-request rate
- Defect escapes (production) — integrate with existing quality systems

### Reliability

- Change failure rate
- Rollback frequency
- Agent task failure rate

### Security

- Security check pass rate
- Blocked critical actions
- Secret-scanning findings

### Governance

- Policy violations
- Approvals requested vs. granted
- High-risk task percentage
- Bypass/exception count

### Developer Experience

- Time-to-first-review
- Surveyed friction of approval gates
- Perceived usefulness of agent plans

### Business Value

- Lead time for selected value-stream changes
- Cost avoidance from prevented incidents (carefully attributed)
- Adoption of governed workflows vs. shadow AI

## Why LOC and commit counts are poor productivity metrics

Lines of code and commit volume reward verbosity and churn. Agentic systems can generate large diffs quickly without improving customer outcomes. Prefer **outcome and risk-adjusted flow metrics**.

## Simulated productivity model used here

The dashboard includes:

- `estimated_manual_minutes`
- `ai_assisted_minutes`
- `estimated_minutes_saved`
- `productivity_gain_percent`

These are **simulated estimates** for illustrating executive reporting patterns. They are not experimentally validated research results and must not be cited as empirical proof of ROI.

## Operating cadence

1. Weekly: platform reviews policy blocks and false positives
2. Monthly: engineering leadership reviews scorecard trends
3. Quarterly: governance board recalibrates risk thresholds and maturity targets
