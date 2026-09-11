"""End-to-end API tests."""
import io
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import init_db


client = TestClient(app)


def setup_module(module):
    init_db()


def test_health():
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_process_rejects_unsupported_type():
    fake = io.BytesIO(b"plain text not a pdf")
    r = client.post(
        "/api/v1/documents/process",
        files={"file": ("test.txt", fake, "text/plain")},
        data={"document_type": "invoice"},
    )
    # Our app returns 400 for unsupported type OR 422 for bad body
    assert r.status_code in (400, 422)
    # If 400, expect a structured error
    if r.status_code == 400:
        body = r.json()
        assert "detail" in body or "error" in body


def test_process_rejects_corrupt_pdf():
    bad_pdf = io.BytesIO(b"%PDF-1.4 this is not really a pdf")
    r = client.post(
        "/api/v1/documents/process",
        files={"file": ("bad.pdf", bad_pdf, "application/pdf")},
        data={"document_type": "invoice"},
    )
    assert r.status_code in (400, 422, 500)


def test_list_documents():
    r = client.get("/api/v1/documents")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_by_name_not_found():
    r = client.get("/api/v1/documents/nonexistent_xyz.pdf")
    assert r.status_code == 404