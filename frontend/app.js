const API = "http://127.0.0.1:8080/api";
const state = {
  learners: [],
  competencies: [],
  assessments: [],
  credentials: [],
  audit: [],
};

const $ = (selector) => document.querySelector(selector);

async function api(path, options = {}) {
  const response = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Request failed" }));
    throw new Error(error.error || "Request failed");
  }
  return response.json();
}

async function refresh() {
  try {
    const [overview, learners, competencies, assessments, credentials, audit] = await Promise.all([
      api("/overview"),
      api("/learners"),
      api("/competencies"),
      api("/assessments"),
      api("/credentials"),
      api("/audit-log"),
    ]);
    state.learners = learners;
    state.competencies = competencies;
    state.assessments = assessments;
    state.credentials = credentials;
    state.audit = audit;
    renderStatus(true);
    renderMetrics(overview);
    renderSelectors();
    renderSteps();
    renderAssessments();
    renderCredentials();
    renderAudit();
  } catch (error) {
    renderStatus(false, error.message);
  }
}

function renderStatus(ok, message = "") {
  $(".dot").classList.toggle("ok", ok);
  $("#apiStatus").textContent = ok ? "API online" : `API offline ${message ? "- " + message : ""}`;
}

function renderMetrics(overview) {
  const labels = [
    ["Learners", overview.learners],
    ["Competencies", overview.competencies],
    ["Assessments", overview.assessments],
    ["Verified", overview.verified],
    ["Credentials", overview.credentials],
    ["Average score", overview.average_score],
    ["Risk queue", overview.risk_queue],
    ["Compliance", overview.compliance_ready ? "Ready" : "Review"],
  ];
  const template = $("#metricTemplate");
  const metrics = $("#overview");
  metrics.innerHTML = "";
  labels.forEach(([label, value]) => {
    const node = template.content.cloneNode(true);
    node.querySelector("strong").textContent = value;
    node.querySelector("small").textContent = label;
    metrics.appendChild(node);
  });
}

function renderSelectors() {
  const learnerSelect = $("#learnerSelect");
  const competencySelect = $("#competencySelect");
  learnerSelect.innerHTML = state.learners
    .map((item) => `<option value="${item.id}">${item.name} - ${item.role}</option>`)
    .join("");
  competencySelect.innerHTML = state.competencies
    .map((item) => `<option value="${item.id}">${item.name} (${item.vertical})</option>`)
    .join("");
}

function selectedCompetency() {
  return state.competencies.find((item) => item.id === $("#competencySelect").value) || state.competencies[0];
}

function renderSteps() {
  const competency = selectedCompetency();
  const list = $("#stepChecklist");
  if (!competency) {
    list.innerHTML = "";
    return;
  }
  list.innerHTML = `<legend>${competency.name} steps</legend>` + competency.steps
    .map((step, index) => `
      <label class="step-row">
        <input type="checkbox" value="${step}" ${index < 4 ? "checked" : ""}>
        ${step}
      </label>
    `)
    .join("");
}

function renderAssessments() {
  $("#assessmentList").innerHTML = state.assessments
    .slice()
    .reverse()
    .map((item) => `
      <article class="assessment">
        <div class="row">
          <div>
            <strong>${item.learner?.name || item.learner_id}</strong>
            <small>${item.competency?.name || item.competency_id}</small>
          </div>
          <span class="badge ${item.status}">${item.status.replaceAll("_", " ")}</span>
        </div>
        <div class="row">
          <span class="score">${item.score}/100</span>
          ${item.status === "verified" ? `<button class="secondary" data-issue="${item.id}">Issue credential</button>` : ""}
        </div>
        <p>${item.explanation}</p>
        <small>${item.coach_action}</small>
      </article>
    `)
    .join("");
  document.querySelectorAll("[data-issue]").forEach((button) => {
    button.addEventListener("click", () => issueCredential(button.dataset.issue));
  });
}

function renderCredentials() {
  $("#credentialList").innerHTML = state.credentials.length
    ? state.credentials.map((item) => `
      <article class="credential">
        <strong>${item.title}</strong>
        <small>${item.learner_id} | ${item.chain}</small>
        <code>${item.proof_hash}</code>
      </article>
    `).join("")
    : "<p>No credentials issued yet.</p>";
}

function renderAudit() {
  $("#auditLog").innerHTML = state.audit
    .slice()
    .reverse()
    .map((item) => `
      <article class="audit-item">
        <div class="row">
          <strong>${item.action}</strong>
          <small>${new Date(item.created_at).toLocaleString()}</small>
        </div>
        <small>${JSON.stringify(item.details)}</small>
      </article>
    `)
    .join("");
}

async function createAssessment(event) {
  event.preventDefault();
  const observed_steps = Array.from(document.querySelectorAll("#stepChecklist input:checked")).map((input) => input.value);
  const payload = {
    learner_id: $("#learnerSelect").value,
    competency_id: $("#competencySelect").value,
    observed_steps,
    evidence_quality: Number($("#evidenceQuality").value),
    safety_events: Number($("#safetyEvents").value),
    human_review_required: $("#humanReview").checked,
    evidence: {
      source: "browser-simulation",
      mode: "multimodal-pilot",
      captured_at: new Date().toISOString(),
    },
  };
  try {
    await api("/assessments", { method: "POST", body: JSON.stringify(payload) });
    await refresh();
  } catch (error) {
    alert(error.message);
  }
}

async function issueCredential(assessmentId) {
  try {
    await api("/credentials/issue", {
      method: "POST",
      body: JSON.stringify({ assessment_id: assessmentId }),
    });
    await refresh();
  } catch (error) {
    alert(error.message);
  }
}

$("#assessmentForm").addEventListener("submit", createAssessment);
$("#competencySelect").addEventListener("change", renderSteps);
$("#refreshBtn").addEventListener("click", refresh);
$("#evidenceQuality").addEventListener("input", (event) => {
  $("#qualityValue").textContent = event.target.value;
});

refresh();
