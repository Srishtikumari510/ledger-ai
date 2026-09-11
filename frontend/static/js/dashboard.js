const API_BASE = "";

const form = document.getElementById("uploadForm");
const fileInput = document.getElementById("fileInput");
const documentType = document.getElementById("documentType");
const statusMsg = document.getElementById("statusMsg");
const processBtn = document.getElementById("processBtn");
const docsBody = document.getElementById("docsBody");
const refreshBtn = document.getElementById("refreshBtn");

function setStatus(msg, kind) {
  statusMsg.textContent = msg;
  statusMsg.className = "status-msg" + (kind ? " " + kind : "");
}

async function loadDocuments() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/documents`);
    if (!res.ok) throw new Error("Failed to load documents");
    const docs = await res.json();
    renderDocs(docs);
  } catch (e) {
    docsBody.innerHTML = `<tr><td colspan="5" class="empty">Error: ${e.message}</td></tr>`;
  }
}

function renderDocs(docs) {
  if (!docs.length) {
    docsBody.innerHTML = `<tr><td colspan="5" class="empty">No documents processed yet.</td></tr>`;
    return;
  }
  docsBody.innerHTML = docs.map(d => `
    <tr>
      <td>${escapeHtml(d.document_name)}</td>
      <td>${escapeHtml(d.document_type)}</td>
      <td><span class="badge ${d.processing_status}">${d.processing_status}</span></td>
      <td>${new Date(d.processed_at).toLocaleString()}</td>
      <td><a href="/result/${encodeURIComponent(d.document_name)}">View &rarr;</a></td>
    </tr>
  `).join("");
}

function escapeHtml(s) {
  if (s == null) return "";
  return String(s).replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[c]));
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const file = fileInput.files[0];
  if (!file) return;

  processBtn.disabled = true;
  setStatus("Processing... this may take 10-30 seconds.", null);

  const fd = new FormData();
  fd.append("file", file);
  fd.append("document_type", documentType.value);

  try {
    const res = await fetch(`${API_BASE}/api/v1/documents/process`, {
      method: "POST",
      body: fd,
    });
    const data = await res.json();
    if (!res.ok) {
      const detail = data.detail || data.error || { message: "Unknown error" };
      setStatus(`Failed: ${detail.code || ""} ${detail.message || JSON.stringify(detail)}`, "error");
    } else {
      setStatus(`Success! Status: ${data.processing_status}. Redirecting...`, "success");
      setTimeout(() => {
        window.location.href = `/result/${encodeURIComponent(data.document_name)}`;
      }, 800);
    }
    loadDocuments();
  } catch (err) {
    setStatus(`Network error: ${err.message}`, "error");
  } finally {
    processBtn.disabled = false;
  }
});

refreshBtn.addEventListener("click", loadDocuments);
loadDocuments();