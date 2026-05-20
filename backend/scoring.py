def score_assessment(payload, competency):
    """Deterministic scoring layer for explainable pilot assessments."""
    observed_steps = set(payload.get("observed_steps", []))
    expected_steps = competency.get("steps", [])
    evidence_quality = payload.get("evidence_quality", 0)
    safety_events = max(0, int(payload.get("safety_events", 0)))
    human_review = bool(payload.get("human_review_required", False))

    if not expected_steps:
        step_score = 0
    else:
        completed = sum(1 for step in expected_steps if step in observed_steps)
        step_score = (completed / len(expected_steps)) * 70

    quality_score = min(max(float(evidence_quality), 0), 100) * 0.25
    safety_penalty = min(safety_events * 12, 30)
    review_penalty = 8 if human_review else 0
    final_score = round(max(0, min(100, step_score + quality_score - safety_penalty - review_penalty)))

    missing_steps = [step for step in expected_steps if step not in observed_steps]
    if safety_events:
        status = "blocked"
    elif human_review:
        status = "human_review"
    elif final_score >= competency.get("required_score", 80):
        status = "verified"
    else:
        status = "coaching_required"

    explanation = build_explanation(final_score, status, missing_steps, safety_events, human_review)
    coach_action = build_coach_action(status, missing_steps)
    return {
        "score": final_score,
        "status": status,
        "missing_steps": missing_steps,
        "explanation": explanation,
        "coach_action": coach_action,
    }


def build_explanation(score, status, missing_steps, safety_events, human_review):
    parts = [f"Deterministic assessment score is {score}."]
    if missing_steps:
        parts.append("Missing or weak steps: " + ", ".join(missing_steps) + ".")
    else:
        parts.append("All expected workflow steps were observed.")
    if safety_events:
        parts.append(f"{safety_events} safety event(s) require review.")
    if human_review:
        parts.append("Human review was requested because confidence or policy thresholds were not met.")
    parts.append(f"Outcome: {status.replace('_', ' ')}.")
    return " ".join(parts)


def build_coach_action(status, missing_steps):
    if status == "verified":
        return "Issue credential and schedule routine recertification."
    if status == "blocked":
        return "Stop certification, open safety review, and assign supervised remediation."
    if status == "human_review":
        return "Route evidence packet to reviewer before credential decision."
    if missing_steps:
        return "Assign micro-drills for: " + ", ".join(missing_steps) + "."
    return "Assign adaptive coaching simulation and reassess."
