# SkillSphere OS

SkillSphere OS is an AI-native workforce skill verification prototype. It includes a local backend API, a static browser dashboard, deterministic competency scoring, audit logging, and tamper-evident credential issuing.

This project is intentionally dependency-light so it can run from the ZIP without `npm install` or `pip install`.

## Features

- Learner and competency graph management
- Explainable assessment scoring
- Coaching recommendations
- Compliance-style audit trail
- Verifiable credential hashes
- Static frontend dashboard
- Standard-library Python backend
- Built-in tests

## Quick Start

1. Open PowerShell in this folder.
2. Run:

```powershell
.\scripts\start.ps1
```

3. Open:

```text
http://127.0.0.1:8080/api/health
```

4. Open the frontend file in a browser:

```text
frontend/index.html
```

The frontend talks to the local API at `http://127.0.0.1:8080/api`.

## Run Tests

```powershell
.\scripts\test.ps1
```

## Project Structure

```text
backend/
  server.py          Local HTTP API
  scoring.py         Deterministic assessment scoring
  credentials.py     Tamper-evident credential generation
  store.py           JSON data persistence
  tests/             Unit tests
frontend/
  index.html         Main dashboard
  styles.css         Responsive UI styling
  app.js             Browser app logic
docs/
  ARCHITECTURE.md
  API.md
scripts/
  start.ps1
  test.ps1
```

## MVP Scope

This is a complete local prototype, not a production SaaS deployment. It is designed as a strong foundation for the first investor/customer demo of:

- Manufacturing QA training
- IT service desk validation
- Compliance-ready skill verification
- Portable credential proof

