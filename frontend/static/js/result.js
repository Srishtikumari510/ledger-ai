const API_BASE = "";
const pathParts = window.location.pathname.split("/");
const documentName = decodeURIComponent(pathParts[pathParts.length - 1]);

function escapeHtml(s) {
  if (s == null) return "";
  return String(s).replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[c]));
}

function unwrap(field) {
  if (field && typeof field === "object" && "value" in field) return field.value;
  return field;
}

function render() {
  fetch(`${API_BASE}/api/v1/documents/${encodeURIComponent(documentName)}`)
    .then(r => {
      if (!r.ok) throw new Error("Not found");
      return r.json();
    })
    .then(data => {
      document.getElementById("docTitle").textContent = data.document_name;
      renderMeta(data);
      renderFileValidation(data.file_validation);
      renderExtracted(data.extracted_data);
      renderValidation(data.validation);
      renderMetadata(data.processing_metadata);
      document.getElementById("rawJson").textContent = JSON.stringify(data, null, 2);
    })
    .catch(e => {
      document.getElementById("docTitle").textContent = `Error: ${e.message}`;
    });
}

function renderMeta(data) {
  document.getElementById("metaBlock").innerHTML = `
    <div><span class="label">Type:</span> <strong>${escapeHtml(data.document_type)}</strong></div>
    <div><span class="label">Status:</span> <span class="badge ${data.processing_status}">${data.processing_status}</span></div>
    <div><span class="label">Confidence:</span> ${data.overall_confidence ?? "N/A"}</div>
    <div><span class="label">Processed:</span> ${escapeHtml(data.processing_metadata.processed_at)}</div>
  `;
}

function renderFileValidation(fv) {
  if (!fv) { document.getElementById("fileValidation").innerHTML = "<em>None</em>"; return; }
  document.getElementById("fileValidation").innerHTML = `
    <table class="kv-table">
      <tr><td class="k">File type</td><td class="v">${escapeHtml(fv.file_type)}</td></tr>
      <tr><td class="k">Supported</td><td class="v">${fv.is_supported}</td></tr>
      <tr><td class="k">Readable</td><td class="v">${fv.is_readable}</td></tr>
      <tr><td class="k">Pages</td><td class="v">${fv.page_count}</td></tr>
      <tr><td class="k">Status</td><td class="v"><span class="badge ${fv.status}">${fv.status}</span></td></tr>
    </table>
  `;
}

function renderExtracted(extracted) {
  const container = document.getElementById("extractedFields");
  const lineItemsEl = document.getElementById("lineItems");

  const scalars = [];
  const arrays = [];
  Object.entries(extracted || {}).forEach(([k, v]) => {
    if (Array.isArray(v)) arrays.push([k, v]);
    else scalars.push([k, v]);
  });

  container.innerHTML = scalars.map(([k, v]) => {
    const value = unwrap(v);
    const isNull = value === null || value === undefined;
    const page = (v && typeof v === "object" && v.page_number) ? ` <small>(p.${v.page_number})</small>` : "";
    return `<tr>
      <td class="k">${escapeHtml(k)}${page}</td>
      <td class="v ${isNull ? "missing" : ""}">${isNull ? "â€” missing â€”" : escapeHtml(typeof value === "object" ? JSON.stringify(value) : value)}</td>
    </tr>`;
  }).join("") || "<tr><td class='empty'>No scalar fields</td></tr>";

  if (arrays.length === 0) {
    lineItemsEl.innerHTML = "<em>No line items or tables found.</em>";
    return;
  }

  lineItemsEl.innerHTML = arrays.map(([k, arr]) => {
    if (!arr.length) return `<h3>${escapeHtml(k)}</h3><em>Empty</em>`;
    const sample = arr[0];
    if (typeof sample !== "object" || sample === null) {
      return `<h3>${escapeHtml(k)}</h3><pre>${escapeHtml(JSON.stringify(arr, null, 2))}</pre>`;
    }
    const cols = Object.keys(sample);
    const rows = arr.map(row => `
      <tr>${cols.map(c => `<td>${escapeHtml(typeof row[c] === "object" ? JSON.stringify(row[c]) : row[c])}</td>`).join("")}</tr>
    `).join("");
    return `
      <h3>${escapeHtml(k)}</h3>
      <table class="kv-table">
        <thead><tr>${cols.map(c => `<th>${escapeHtml(c)}</th>`).join("")}</tr></thead>
        <tbody>${rows}</tbody>
      </table>`;
  }).join("");
}

function renderValidation(validation) {
  const el = document.getElementById("validationBlock");
  if (!validation) { el.innerHTML = "<em>No validation data.</em>"; return; }
  const checks = validation.checks || [];
  if (!checks.length) {
    el.innerHTML = `<p>Overall: <span class="badge ${validation.overall_status}">${validation.overall_status}</span></p><em>No checks applicable.</em>`;
    return;
  }
  el.innerHTML = `
    <p><strong>Overall:</strong> <span class="badge ${validation.overall_status}">${validation.overall_status}</span></p>
    ${checks.map(c => `
      <div class="check ${c.status}">
        <div class="name">${escapeHtml(c.name)} <span class="badge ${c.status}">${c.status}</span></div>
        <div class="formula">${escapeHtml(c.formula)}</div>
        <div class="nums">
          calculated: <strong>${c.calculated_value ?? "â€”"}</strong> |
          reported: <strong>${c.reported_value ?? "â€”"}</strong> |
          variance: <strong>${c.variance ?? "â€”"}</strong>
        </div>
      </div>
    `).join("")}
  `;
}

function renderMetadata(meta) {
  if (!meta) { document.getElementById("metadataBlock").innerHTML = "<em>None</em>"; return; }
  document.getElementById("metadataBlock").innerHTML = `
    <table class="kv-table">
      <tr><td class="k">OCR used</td><td class="v">${meta.ocr_used}</td></tr>
      <tr><td class="k">LLM used</td><td class="v">${meta.llm_used}</td></tr>
      <tr><td class="k">Provider</td><td class="v">${escapeHtml(meta.llm_provider || "â€”")}</td></tr>
      <tr><td class="k">Model</td><td class="v">${escapeHtml(meta.llm_model || "â€”")}</td></tr>
      <tr><td class="k">Processing time</td><td class="v">${meta.processing_time_ms} ms</td></tr>
    </table>
  `;
}

document.getElementById("toggleRaw").addEventListener("click", () => {
  const el = document.getElementById("rawJson");
  el.classList.toggle("hidden");
  document.getElementById("toggleRaw").textContent =
    el.classList.contains("hidden") ? "Show Raw JSON" : "Hide Raw JSON";
});

render();
