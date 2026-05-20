# API Reference

Base URL:

```text
http://127.0.0.1:8080/api
```

## GET /health

Returns service status.

## GET /overview

Returns dashboard metrics.

## GET /learners

Returns learner records.

## GET /competencies

Returns competency graph records.

## GET /assessments

Returns enriched assessment records.

## POST /assessments

Creates an explainable assessment.

Example body:

```json
{
  "learner_id": "LRN-1001",
  "competency_id": "CMP-MFG-001",
  "observed_steps": ["PPE check", "Tool inspection", "Calibration confirmation"],
  "evidence_quality": 86,
  "safety_events": 0,
  "human_review_required": false
}
```

## POST /credentials/issue

Issues a credential for a verified assessment.

Example body:

```json
{
  "assessment_id": "ASM-9001"
}
```

## GET /credentials

Returns issued credentials.

## GET /verify?hash={proof_hash}

Verifies a credential proof hash.

## GET /audit-log

Returns audit events.

