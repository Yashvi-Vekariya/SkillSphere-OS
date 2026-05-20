import hashlib
from datetime import datetime, timedelta, timezone


def issue_credential(learner, competency, assessment):
    issued_at = datetime.now(timezone.utc)
    expires_at = issued_at + timedelta(days=365)
    subject = f"{learner['id']}|{competency['id']}|{assessment['id']}|{assessment['score']}|{issued_at.isoformat()}"
    proof_hash = hashlib.sha256(subject.encode("utf-8")).hexdigest()
    return {
        "id": "CRD-" + proof_hash[:10].upper(),
        "learner_id": learner["id"],
        "competency_id": competency["id"],
        "assessment_id": assessment["id"],
        "title": competency["name"],
        "issuer": "SkillSphere OS Trust Layer",
        "proof_hash": proof_hash,
        "chain": "local-tamper-evident-ledger",
        "issued_at": issued_at.isoformat(),
        "expires_at": expires_at.isoformat(),
    }
