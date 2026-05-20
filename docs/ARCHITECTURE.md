# Architecture

SkillSphere OS uses a layered prototype architecture:

1. Frontend dashboard
2. API orchestration layer
3. Deterministic scoring engine
4. Credential trust layer
5. Audit and local data persistence

## Assessment Loop

```text
Observe -> Evaluate -> Coach -> Verify -> Credential -> Audit
```

## Key Design Decisions

- The scoring engine is deterministic and explainable.
- The credential layer uses SHA-256 proof hashes as a local tamper-evident stand-in for blockchain anchoring.
- The audit trail records assessment and credential events.
- The frontend is static so it does not require a build system.
- The backend uses only Python standard-library modules.

## Production Expansion Path

- Replace local JSON persistence with PostgreSQL.
- Add FastAPI or Django for authentication, RBAC, and OpenAPI docs.
- Connect real CV/audio evidence services behind the scoring contract.
- Add human-review queues for low-confidence assessments.
- Anchor credential hashes to Hyperledger Fabric or Polygon.
- Add federated learning and edge inference per plant/site.

