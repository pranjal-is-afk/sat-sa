// SAT-SA Air-Gapped Supervisory Console Client Logic
let currentFindingId = null;

// Tab Navigation
function switchTab(tabId) {
  document.querySelectorAll(".tab-content").forEach(el => el.classList.remove("active"));
  document.querySelectorAll(".nav-tab").forEach(el => el.classList.remove("active"));
  
  const target = document.getElementById("tab-" + tabId);
  if (target) target.classList.add("active");
  
  const tabs = document.querySelectorAll(".nav-tab");
  tabs.forEach(tab => {
    if (tab.getAttribute("onclick").includes(tabId)) {
      tab.classList.add("active");
    }
  });

  if (tabId === "portfolio") loadPortfolioData();
  if (tabId === "entity-profile") loadEntityDeepDive(document.getElementById("entity-selector").value);
  if (tabId === "review-queue") loadReviewQueue();
  if (tabId === "submissions") loadSubmissions();
  if (tabId === "audit") loadAuditTrail();
}

// Initial Load
document.addEventListener("DOMContentLoaded", () => {
  loadPortfolioData();
});

// Load Portfolio Overview
async function loadPortfolioData() {
  try {
    const statsRes = await fetch("/api/v1/admin/stats");
    const stats = await statsRes.json();
    
    document.getElementById("kpi-cses").innerText = stats.cses || 10;
    document.getElementById("kpi-alerts").innerText = (stats.alerts || 0).toLocaleString();
    document.getElementById("kpi-gaps").innerText = (stats.findings || 0).toLocaleString();
    document.getElementById("kpi-queue").innerText = (stats.findings - stats.dispositions) || 0;

    loadEntityRanking();
  } catch (err) {
    console.error("Failed to load portfolio stats:", err);
  }
}

// Load Entity Ranking
async function loadEntityRanking() {
  try {
    const res = await fetch("/api/v1/entities/ranking");
    const rankings = await res.json();

    const tbody = document.getElementById("ranking-table-body");
    tbody.innerHTML = "";

    rankings.forEach((ent, idx) => {
      const score = ent.score || 0;
      let barColor = "#10b981"; // Low
      let badgeClass = "badge-low";
      if (score >= 70) { barColor = "#ef4444"; badgeClass = "badge-critical"; }
      else if (score >= 45) { barColor = "#f59e0b"; badgeClass = "badge-high"; }
      else if (score >= 20) { barColor = "#3b82f6"; badgeClass = "badge-medium"; }

      let contributorPills = "";
      if (ent.contributors && ent.contributors.length > 0) {
        contributorPills = ent.contributors.slice(0, 2).map(c => 
          `<span class="badge ${badgeClass}" style="margin-right: 4px; font-size: 10px;">${c.percentage}% ${c.factor}</span>`
        ).join("");
      } else {
        contributorPills = `<span class="badge badge-low">Normal Operations</span>`;
      }

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td style="font-weight: 700;">#${idx + 1}</td>
        <td><strong>${ent.cse_id}</strong></td>
        <td>${ent.name}</td>
        <td>${ent.sector}</td>
        <td><span class="badge badge-medium">${ent.criticality_tier}</span></td>
        <td>
          <div class="risk-bar-container">
            <div class="risk-bar" style="width: ${Math.min(100, score)}%; background: ${barColor};"></div>
          </div>
          <strong>${score}</strong>/100
        </td>
        <td>${contributorPills}</td>
        <td>
          <button class="btn btn-outline" style="padding: 4px 8px; font-size: 11px;" onclick="inspectFromRanking('${ent.cse_id}')">
            Deep Dive
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Failed to load ranking:", err);
  }
}

function inspectFromRanking(cseId) {
  document.getElementById("entity-selector").value = cseId;
  switchTab("entity-profile");
}

// Load Entity Deep Dive
async function loadEntityDeepDive(cseId) {
  try {
    const res = await fetch(`/api/v1/entities/${cseId}`);
    const data = await res.json();

    const risk = data.risk_profile || {};
    const score = risk.score || 0;
    document.getElementById("deep-score").innerText = `${score}/100 (${risk.risk_tier || 'LOW'})`;
    document.getElementById("deep-score").style.color = score >= 50 ? "#ef4444" : "#10b981";

    // Contributor Breakdown
    const contContainer = document.getElementById("contributors-container");
    contContainer.innerHTML = "";

    const contributors = risk.contributors || [];
    if (contributors.length === 0) {
      contContainer.innerHTML = `<p style="color: var(--text-muted); font-size: 13px;">No supervisory risk factors detected for this entity.</p>`;
    } else {
      contributors.forEach(c => {
        const item = document.createElement("div");
        item.style.marginBottom = "10px";
        item.innerHTML = `
          <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 3px;">
            <span>${c.factor}</span>
            <strong>${c.percentage}%</strong>
          </div>
          <div style="width: 100%; height: 6px; background: #334155; border-radius: 3px; overflow: hidden;">
            <div style="width: ${c.percentage}%; height: 100%; background: var(--accent-cyan);"></div>
          </div>
        `;
        contContainer.appendChild(item);
      });
    }

    // Peer Comparison
    const peerRes = await fetch(`/api/v1/entities/${cseId}/peer-comparison`);
    const peer = await peerRes.json();
    const entM = peer.entity_metrics;
    const baseM = peer.peer_sector_baseline;

    document.getElementById("peer-comparison-container").innerHTML = `
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 10px;">
        <div style="background: #0f172a; padding: 12px; border-radius: 6px;">
          <div style="font-size: 11px; color: var(--text-muted);">Median Alert Closure</div>
          <div style="font-size: 18px; font-weight: bold; color: ${entM.closure_median_mins < baseM.peer_p05_closure_mins ? '#ef4444' : '#fff'};">
            ${entM.closure_median_mins} mins
          </div>
          <div style="font-size: 11px; color: var(--text-secondary);">Sector Median: ${baseM.sector_median_closure_mins} mins</div>
        </div>
        <div style="background: #0f172a; padding: 12px; border-radius: 6px;">
          <div style="font-size: 11px; color: var(--text-muted);">Critical Escalation Rate</div>
          <div style="font-size: 18px; font-weight: bold; color: #fff;">
            ${Math.round((entM.escalations / Math.max(1, entM.critical_alerts)) * 100)}%
          </div>
          <div style="font-size: 11px; color: var(--text-secondary);">Sector Peer Target: ${Math.round(baseM.peer_critical_escalation_rate * 100)}%</div>
        </div>
      </div>
    `;

    // Load Entity Findings
    const fRes = await fetch(`/api/v1/findings?cse_id=${cseId}&limit=20`);
    const findings = await fRes.json();
    const fBody = document.getElementById("entity-findings-body");
    fBody.innerHTML = "";

    findings.forEach(f => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong>${f.finding_id}</strong></td>
        <td><span class="badge badge-${f.severity.toLowerCase()}">${f.severity}</span></td>
        <td>${f.category}</td>
        <td>${f.reason}</td>
        <td><code>${f.rule_id}</code></td>
        <td>
          <button class="btn btn-outline" style="padding: 3px 8px; font-size: 11px;" onclick="openFindingModal('${f.finding_id}')">Inspect</button>
        </td>
      `;
      fBody.appendChild(tr);
    });

  } catch (err) {
    console.error("Failed to load entity detail:", err);
  }
}

// Load Prioritized Review Queue
async function loadReviewQueue() {
  const sev = document.getElementById("filter-severity").value;
  const cat = document.getElementById("filter-category").value;

  let url = "/api/v1/findings/queue?limit=40";
  if (sev) url += `&severity=${sev}`;
  if (cat) url += `&category=${encodeURIComponent(cat)}`;

  try {
    const res = await fetch(url);
    const queue = await res.json();
    const tbody = document.getElementById("queue-table-body");
    tbody.innerHTML = "";

    if (queue.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-muted);">No pending review items found.</td></tr>`;
      return;
    }

    queue.forEach(item => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td style="font-weight: 700; color: var(--accent-cyan);">${item.priority_score || '--'}</td>
        <td><strong>${item.cse_id}</strong></td>
        <td><span class="badge badge-${item.severity.toLowerCase()}">${item.severity}</span></td>
        <td>${item.category}</td>
        <td><code>${item.alert_id || item.asset_id || item.case_id || '--'}</code></td>
        <td>${item.reason}</td>
        <td>${Math.round((item.confidence || 0.8) * 100)}%</td>
        <td>
          <button class="btn" style="padding: 4px 10px; font-size: 11px;" onclick="openFindingModal('${item.finding_id}')">Drill Down</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Failed to load queue:", err);
  }
}

// Open Finding Drill-Down Modal
async function openFindingModal(findingId) {
  currentFindingId = findingId;
  try {
    const res = await fetch(`/api/v1/findings/${findingId}`);
    const data = await res.json();
    const f = data.finding;

    document.getElementById("drawer-finding-id").innerText = f.finding_id;
    document.getElementById("drawer-category-badge").innerText = f.category;
    document.getElementById("drawer-category-badge").className = `badge badge-${f.severity.toLowerCase()}`;
    document.getElementById("drawer-rule-version").innerText = `Rule: ${f.rule_id} (Engine v${f.rule_version})`;
    document.getElementById("drawer-reason").innerText = f.reason;
    document.getElementById("drawer-baseline").innerText = f.peer_baseline || "Standard operational baseline";
    document.getElementById("drawer-action").innerText = f.recommended_action;

    // Evidence Table
    const evBody = document.getElementById("drawer-evidence-body");
    evBody.innerHTML = "";
    (f.evidence || []).forEach(ev => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><code>${ev.table}</code></td>
        <td><strong>${ev.record_id || 'N/A'}</strong></td>
        <td>${ev.field}</td>
        <td><span style="color: var(--accent-cyan); font-weight: 600;">${ev.value}</span></td>
      `;
      evBody.appendChild(tr);
    });

    // Timeline
    const tlContainer = document.getElementById("drawer-timeline");
    tlContainer.innerHTML = "";
    (data.timeline || []).forEach(t => {
      const item = document.createElement("div");
      item.className = "timeline-item";
      item.innerHTML = `
        <div class="timeline-time">${t.time || ''}</div>
        <div class="timeline-event">${t.event}</div>
        <div class="timeline-detail">${t.details || ''}</div>
      `;
      tlContainer.appendChild(item);
    });

    document.getElementById("finding-modal").classList.add("active");
  } catch (err) {
    console.error("Failed to open finding modal:", err);
  }
}

function closeFindingModal(e) {
  if (e.target.id === "finding-modal") {
    closeModalDirect();
  }
}

function closeModalDirect() {
  document.getElementById("finding-modal").classList.remove("active");
  currentFindingId = null;
}

// Submit Human Disposition
async function submitDisposition() {
  if (!currentFindingId) return;
  const decision = document.getElementById("disp-decision").value;
  const comment = document.getElementById("disp-comment").value.trim();

  if (comment.length < 5) {
    alert("Please provide supervisory comments/instructions before recording disposition.");
    return;
  }

  try {
    const res = await fetch(`/api/v1/findings/${currentFindingId}/disposition`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: jsonStr({
        decision: decision,
        comment: comment,
        reviewer_id: "EXAMINER-LEAD"
      })
    });
    const result = await res.json();
    alert(`Disposition recorded successfully!\nAudit Block Hash: ${result.audit_hash.slice(0, 16)}...`);
    closeModalDirect();
    loadReviewQueue();
  } catch (err) {
    alert("Failed to record disposition: " + err);
  }
}

// Submissions Manager
async function loadSubmissions() {
  try {
    const res = await fetch("/api/v1/submissions");
    const list = await res.json();
    const tbody = document.getElementById("submissions-table-body");
    tbody.innerHTML = "";

    list.forEach(s => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong>${s.submission_id}</strong></td>
        <td>${s.entity_name || s.cse_id}</td>
        <td>${s.reporting_period}</td>
        <td>${s.uploaded_at}</td>
        <td>${s.uploader_id}</td>
        <td>${s.file_count} files</td>
        <td><span class="badge badge-confirmed">${s.status}</span></td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Failed to load submissions:", err);
  }
}

// Batch File Upload
async function submitFiles() {
  const cseId = document.getElementById("upload-cse-id").value;
  const period = document.getElementById("upload-period").value;
  const fileInput = document.getElementById("upload-files");

  if (!fileInput.files.length) {
    alert("Please select CSV or JSON files to upload.");
    return;
  }

  const formData = new FormData();
  formData.append("cse_id", cseId);
  formData.append("reporting_period", period);
  formData.append("uploader_id", "SUPERVISOR-WEB");
  for (let i = 0; i < fileInput.files.length; i++) {
    formData.append("files", fileInput.files[i]);
  }

  try {
    const res = await fetch("/api/v1/submissions/upload", {
      method: "POST",
      body: formData
    });
    const result = await res.json();
    alert(`Batch Ingested Successfully!\nValid Alerts: ${result.valid_alerts_count}\nValid Cases: ${result.valid_cases_count}\nData Quality Issues: ${result.data_quality_issues_count}`);
    loadSubmissions();
  } catch (err) {
    alert("Upload failed: " + err);
  }
}

// Cryptographic Audit
async function loadAuditTrail() {
  try {
    const res = await fetch("/api/v1/audit-events?limit=50");
    const events = await res.json();
    const tbody = document.getElementById("audit-table-body");
    tbody.innerHTML = "";

    events.forEach(e => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>#${e.id}</td>
        <td style="font-size: 11px;">${e.timestamp}</td>
        <td><strong>${e.action}</strong></td>
        <td><code>${e.user_id}</code></td>
        <td style="font-family: monospace; font-size: 11px;">${e.prev_hash.slice(0, 14)}...</td>
        <td style="font-family: monospace; font-size: 11px; color: var(--accent-cyan);">${e.hash.slice(0, 14)}...</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Failed to load audit trail:", err);
  }
}

async function verifyChainIntegrity() {
  try {
    const res = await fetch("/api/v1/audit-events/verify-integrity");
    const result = await res.json();
    const banner = document.getElementById("integrity-banner");
    banner.style.display = "block";
    if (result.valid) {
      banner.style.background = "rgba(16, 185, 129, 0.2)";
      banner.style.color = "#10b981";
      banner.style.border = "1px solid #10b981";
      banner.innerHTML = `<strong>VERIFICATION SUCCESSFUL:</strong> ${result.message} Total chained events: ${result.total_events}. Latest hash: <code>${result.latest_hash || ''}</code>`;
    } else {
      banner.style.background = "rgba(239, 68, 68, 0.2)";
      banner.style.color = "#ef4444";
      banner.style.border = "1px solid #ef4444";
      banner.innerHTML = `<strong>INTEGRITY BREACH DETECTED:</strong> ${result.reason}`;
    }
  } catch (err) {
    alert("Integrity verification request failed: " + err);
  }
}

// Reseed Ground Truth
async function reseedDemoData() {
  if (!confirm("Reseed the database from synthetic ground-truth files and re-execute supervisory analytics?")) return;
  try {
    const res = await fetch("/api/v1/admin/reseed", { method: "POST" });
    const result = await res.json();
    alert(`Database Reseeded Successfully!\nGenerated ${result.findings_generated} supervisory findings across ${result.entities_scored} entities.`);
    loadPortfolioData();
  } catch (err) {
    alert("Reseed failed: " + err);
  }
}

function jsonStr(obj) {
  return JSON.stringify(obj);
}
