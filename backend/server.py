from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
import json
import sys

try:
    from .credentials import issue_credential
    from .scoring import score_assessment
    from .store import append_audit, load_data, save_data, utc_now
except ImportError:
    from credentials import issue_credential
    from scoring import score_assessment
    from store import append_audit, load_data, save_data, utc_now


HOST = "127.0.0.1"
PORT = 8080


class SkillSphereHandler(BaseHTTPRequestHandler):
    server_version = "SkillSphereOS/1.0"

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            return self.json_response({"ok": True, "service": "SkillSphere OS", "time": utc_now()})
        if parsed.path == "/api/overview":
            return self.json_response(build_overview(load_data()))
        if parsed.path == "/api/learners":
            return self.json_response(load_data()["learners"])
        if parsed.path == "/api/competencies":
            return self.json_response(load_data()["competencies"])
        if parsed.path == "/api/assessments":
            return self.json_response(enrich_assessments(load_data()))
        if parsed.path == "/api/credentials":
            return self.json_response(load_data()["credentials"])
        if parsed.path == "/api/audit-log":
            return self.json_response(load_data()["audit_log"])
        if parsed.path == "/api/verify":
            query = parse_qs(parsed.query)
            proof_hash = query.get("hash", [""])[0]
            data = load_data()
            credential = next((item for item in data["credentials"] if item["proof_hash"] == proof_hash), None)
            return self.json_response({"valid": bool(credential), "credential": credential})
        return self.json_response({"error": "Not found"}, status=404)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/assessments":
            return self.create_assessment()
        if parsed.path == "/api/credentials/issue":
            return self.create_credential()
        return self.json_response({"error": "Not found"}, status=404)

    def create_assessment(self):
        payload = self.read_json()
        data = load_data()
        learner = find_by_id(data["learners"], payload.get("learner_id"))
        competency = find_by_id(data["competencies"], payload.get("competency_id"))
        if not learner or not competency:
            return self.json_response({"error": "Invalid learner_id or competency_id"}, status=400)
        if not learner.get("consent"):
            return self.json_response({"error": "Learner consent is required before assessment"}, status=409)

        result = score_assessment(payload, competency)
        assessment = {
            "id": f"ASM-{9001 + len(data['assessments'])}",
            "learner_id": learner["id"],
            "competency_id": competency["id"],
            "score": result["score"],
            "status": result["status"],
            "evidence": payload.get("evidence", {}),
            "missing_steps": result["missing_steps"],
            "explanation": result["explanation"],
            "coach_action": result["coach_action"],
            "created_at": utc_now(),
        }
        data["assessments"].append(assessment)
        append_audit(data, "system", "assessment.created", {"assessment_id": assessment["id"]})
        save_data(data)
        return self.json_response(assessment, status=201)

    def create_credential(self):
        payload = self.read_json()
        data = load_data()
        assessment = find_by_id(data["assessments"], payload.get("assessment_id"))
        if not assessment:
            return self.json_response({"error": "Invalid assessment_id"}, status=400)
        if assessment["status"] != "verified":
            return self.json_response({"error": "Only verified assessments can receive credentials"}, status=409)
        existing = next((item for item in data["credentials"] if item["assessment_id"] == assessment["id"]), None)
        if existing:
            return self.json_response(existing)

        learner = find_by_id(data["learners"], assessment["learner_id"])
        competency = find_by_id(data["competencies"], assessment["competency_id"])
        credential = issue_credential(learner, competency, assessment)
        data["credentials"].append(credential)
        append_audit(data, "system", "credential.issued", {"credential_id": credential["id"]})
        save_data(data)
        return self.json_response(credential, status=201)

    def read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        body = self.rfile.read(length).decode("utf-8")
        return json.loads(body)

    def json_response(self, payload, status=200):
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def find_by_id(items, item_id):
    return next((item for item in items if item["id"] == item_id), None)


def enrich_assessments(data):
    learners = {item["id"]: item for item in data["learners"]}
    competencies = {item["id"]: item for item in data["competencies"]}
    enriched = []
    for assessment in data["assessments"]:
        row = dict(assessment)
        row["learner"] = learners.get(assessment["learner_id"], {})
        row["competency"] = competencies.get(assessment["competency_id"], {})
        enriched.append(row)
    return enriched


def build_overview(data):
    assessments = data["assessments"]
    verified = [item for item in assessments if item["status"] == "verified"]
    avg_score = round(sum(item["score"] for item in assessments) / len(assessments), 1) if assessments else 0
    return {
        "learners": len(data["learners"]),
        "competencies": len(data["competencies"]),
        "assessments": len(assessments),
        "verified": len(verified),
        "credentials": len(data["credentials"]),
        "average_score": avg_score,
        "compliance_ready": True,
        "risk_queue": len([item for item in assessments if item["status"] in ("blocked", "human_review")]),
    }


def run():
    httpd = ThreadingHTTPServer((HOST, PORT), SkillSphereHandler)
    print(f"SkillSphere OS API running at http://{HOST}:{PORT}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
