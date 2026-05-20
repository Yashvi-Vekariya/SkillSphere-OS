import json
import os
import threading
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent / "data"
DB_FILE = DATA_DIR / "skillsphere.json"
_LOCK = threading.Lock()


def utc_now():
    return datetime.now(timezone.utc).isoformat()


DEFAULT_DATA = {
    "metadata": {
        "product": "SkillSphere OS",
        "version": "1.0.0",
        "created_at": utc_now(),
    },
    "learners": [
        {
            "id": "LRN-1001",
            "name": "Aarav Mehta",
            "role": "Manufacturing QA Technician",
            "site": "Pune Plant A",
            "language": "Hindi / English",
            "consent": True,
            "risk_flag": "none",
        },
        {
            "id": "LRN-1002",
            "name": "Mira Shah",
            "role": "Service Desk Analyst",
            "site": "Bengaluru Delivery Center",
            "language": "English / Kannada",
            "consent": True,
            "risk_flag": "needs_review",
        },
        {
            "id": "LRN-1003",
            "name": "Jonas Weber",
            "role": "Assembly Line Operator",
            "site": "Stuttgart Partner Lab",
            "language": "German / English",
            "consent": True,
            "risk_flag": "none",
        },
    ],
    "competencies": [
        {
            "id": "CMP-MFG-001",
            "name": "Torque Tool Calibration",
            "vertical": "Manufacturing QA",
            "required_score": 82,
            "steps": [
                "PPE check",
                "Tool inspection",
                "Calibration confirmation",
                "Test fastening",
                "Defect documentation",
            ],
        },
        {
            "id": "CMP-MFG-002",
            "name": "Visual Defect Classification",
            "vertical": "Manufacturing QA",
            "required_score": 80,
            "steps": [
                "Lighting verification",
                "Surface scan",
                "Defect category selection",
                "Severity scoring",
                "Escalation decision",
            ],
        },
        {
            "id": "CMP-IT-001",
            "name": "Service Desk Incident Triage",
            "vertical": "IT Service Desk",
            "required_score": 78,
            "steps": [
                "User verification",
                "Impact assessment",
                "Knowledge base search",
                "Resolution attempt",
                "Escalation notes",
            ],
        },
    ],
    "assessments": [
        {
            "id": "ASM-9001",
            "learner_id": "LRN-1001",
            "competency_id": "CMP-MFG-001",
            "score": 88,
            "status": "verified",
            "evidence": {
                "video": "edge://plant-a/cell-4/session-9001",
                "audio": "clear",
                "sensor": "torque within tolerance",
            },
            "explanation": "All critical steps completed. Minor delay during documentation.",
            "coach_action": "Repeat documentation drill once this week.",
            "created_at": utc_now(),
        },
        {
            "id": "ASM-9002",
            "learner_id": "LRN-1002",
            "competency_id": "CMP-IT-001",
            "score": 73,
            "status": "coaching_required",
            "evidence": {
                "screen": "simulation://incident-bridge/vpn-outage",
                "audio": "n/a",
                "sensor": "n/a",
            },
            "explanation": "Impact assessment was correct, but escalation notes missed timeline details.",
            "coach_action": "Assign escalation-note micro-simulation.",
            "created_at": utc_now(),
        },
    ],
    "credentials": [],
    "audit_log": [],
}


def ensure_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DB_FILE.exists():
        save_data(deepcopy(DEFAULT_DATA))


def load_data():
    ensure_db()
    with _LOCK:
        with DB_FILE.open("r", encoding="utf-8") as handle:
            return json.load(handle)


def save_data(data):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp_file = DB_FILE.with_suffix(".tmp")
    with _LOCK:
        with tmp_file.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
        os.replace(tmp_file, DB_FILE)


def append_audit(data, actor, action, details):
    data["audit_log"].append(
        {
            "id": f"AUD-{len(data['audit_log']) + 1:05d}",
            "actor": actor,
            "action": action,
            "details": details,
            "created_at": utc_now(),
        }
    )
