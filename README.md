\# LedgerAI — Document Intelligence Platform



\*\*Turn complex documents into structured intelligence.\*\*



An end-to-end AI-powered document extraction, validation, and API platform for

financial documents (Invoices, Balance Sheets, Profit \& Loss, Cash Flow Statements).



\---



\## 1. Overview



LedgerAI accepts financial documents as \*\*PDF / JPG / PNG\*\*, validates them, extracts

\*\*every meaningful field and table\*\* using OCR + LLM, runs \*\*deterministic financial

validations\*\*, persists the result, and serves it back through a \*\*consistent REST API\*\*

and a \*\*Jinja2 dashboard\*\*.



The project demonstrates practical AI engineering: turning OCR + LLM capabilities into

a reliable, structured, testable, and deployable application.



\### Live URLs



| Service | URL |

|---|---|

| Landing page | https://ledger-ai-y8ff.onrender.com/ |

| Dashboard | https://ledger-ai-y8ff.onrender.com/dashboard |

| API base | https://ledger-ai-y8ff.onrender.com/api/v1 |

| Health check | https://ledger-ai-y8ff.onrender.com/api/v1/health |

| Swagger / OpenAPI | https://ledger-ai-y8ff.onrender.com/docs |

| GitHub repo | https://github.com/Srishtikumari510/ledger-ai |



> \*\*Note:\*\* The Render free tier puts services to sleep after \~15 minutes of inactivity.

> The first request may take 30–60 seconds to wake the service. This also means the

> SQLite database resets on cold start — processed documents are not retained after sleep.

> This is a known limitation of the free tier and does not affect correctness.



\---



\## 2. Architecture



!\[Architecture](docs/architecture.svg)

┌─────────────────────┐

│ Browser / API │

└──────────┬──────────┘

│ multipart/form-data + document\_type

▼

┌─────────────────────┐

│ FastAPI /api/v1 │ ← routes/documents.py

└──────────┬──────────┘

│

▼

┌─────────────────────┐

│ Document Service │ orchestrator

└──────────┬──────────┘

│

┌─────────┼─────────┬────────────┐

▼ ▼ ▼ ▼

┌───────┐ ┌───────┐ ┌────────┐ ┌──────────┐

│ File │ │ OCR │ │ LLM │ │ Financial│

│ Vali- │ │ Serv- │ │ Extrac-│ │ Valida- │

│ dation│ │ ice │ │ tion │ │ tion │

└───────┘ └───────┘ └────────┘ └──────────┘

│

▼

┌────────────────┐

│ Repository / │ SQLAlchemy

│ SQLite (PG) │

└────────────────┘



text



\*\*Flow per document:\*\*



1\. \*\*Validate\*\* — file type, size, readability, page count (≤ 3)

2\. \*\*Extract text\*\* — native PDF text via `pdfplumber`, fallback to Tesseract OCR

3\. \*\*Extract fields\*\* — LLM (Gemini) with strict JSON schema + page-level evidence

4\. \*\*Validate financials\*\* — deterministic rules per document type

5\. \*\*Persist\*\* — write JSON result to DB

6\. \*\*Respond\*\* — return consistent structured JSON



\---



\## 3. Technology stack



| Layer | Choice | Why |

|---|---|---|

| Web framework | \*\*FastAPI\*\* | Auto-generated Swagger, async, Pydantic validation, great DX |

| Schemas | \*\*Pydantic v2\*\* | Structured typing, automatic validation, JSON serialization |

| Database | \*\*SQLAlchemy + SQLite\*\* | Zero-config dev; swap `DATABASE\_URL` for Postgres in prod |

| OCR | \*\*Tesseract 5.x\*\* | Free, offline, mature, good enough for financial scans |

| PDF → image | \*\*pdf2image + Poppler\*\* | Reliable scanned-PDF handling |

| PDF text | \*\*pdfplumber\*\* | Best native text extraction quality on financial layouts |

| LLM | \*\*Google Gemini\*\* | Free tier, structured JSON output, low latency |

| Frontend | \*\*Jinja2 + vanilla HTML/CSS/JS\*\* | Mandatory requirement; zero build step; fast |

| Deployment | \*\*Render (Docker)\*\* | Free tier, Docker support, easy env-var config |



\---



\## 4. Local setup



\*\*Prerequisites:\*\*

\- Python 3.12

\- Tesseract OCR (system package)

\- Poppler (for `pdf2image`)



\### Windows



```powershell

\# Install external tools (once)

winget install UB-Mannheim.TesseractOCR

winget install oschwartz10612.Poppler



\# Clone and set up

git clone https://github.com/Srishtikumari510/ledger-ai.git

cd ledger-ai/backend

py -3.12 -m venv venv

.\\venv\\Scripts\\Activate.ps1

pip install -r requirements.txt



\# Configure

Copy-Item .env.example .env

notepad .env   # set LLM\_API\_KEY



\# Run

uvicorn app.main:app --reload --port 8000

Linux / macOS

bash

sudo apt-get install -y tesseract-ocr poppler-utils      # Debian/Ubuntu

\# or: brew install tesseract poppler                     # macOS



git clone https://github.com/Srishtikumari510/ledger-ai.git

cd ledger-ai/backend

python3.12 -m venv venv \&\& source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env

\# edit .env with your LLM\_API\_KEY

uvicorn app.main:app --reload --port 8000

Then open:



Landing: http://127.0.0.1:8000/



Dashboard: http://127.0.0.1:8000/dashboard



Swagger: http://127.0.0.1:8000/docs



5\. Environment variables

See backend/.env.example:



env

APP\_NAME=Document Intelligence API

APP\_VERSION=1.0.0

LOG\_LEVEL=INFO



DATABASE\_URL=sqlite:///./documents.db



MAX\_PAGES=3

MAX\_FILE\_SIZE\_MB=20

UPLOAD\_DIR=./uploads



LLM\_PROVIDER=gemini

LLM\_API\_KEY=your\_api\_key\_here

LLM\_MODEL=gemini-2.5-flash



OCR\_PROVIDER=tesseract

OCR\_SPACE\_API\_KEY=

POPPLER\_PATH=

Never commit .env. It is excluded by .gitignore.



Get a free Gemini key: https://aistudio.google.com/app/apikey



6\. API reference

All endpoints are documented at /docs (Swagger UI).



POST /api/v1/documents/process

Upload and process a document.



bash

curl -X POST "https://ledger-ai-y8ff.onrender.com/api/v1/documents/process" \\

&#x20; -F "file=@sample\_invoice.pdf" \\

&#x20; -F "document\_type=invoice"

document\_type must be one of:

invoice | balance\_sheet | profit\_and\_loss | cash\_flow\_statement



GET /api/v1/documents/{document\_name}

Retrieve the latest structured result by exact file name.



bash

curl "https://ledger-ai-y8ff.onrender.com/api/v1/documents/sample\_invoice.pdf"

GET /api/v1/documents

List all processed documents (used by the dashboard).



bash

curl "https://ledger-ai-y8ff.onrender.com/api/v1/documents"

GET /api/v1/health

bash

curl "https://ledger-ai-y8ff.onrender.com/api/v1/health"

\# → {"status":"ok","service":"Document Intelligence API","version":"1.0.0"}

Response shape (abridged)

json

{

&#x20; "document\_name": "sample\_invoice.pdf",

&#x20; "document\_type": "invoice",

&#x20; "processing\_status": "PASS",

&#x20; "file\_validation": { "file\_type": "application/pdf", "page\_count": 1, "status": "PASS" },

&#x20; "extracted\_data": {

&#x20;   "invoice\_number": { "value": "INV-2026-0042", "page\_number": 1 },

&#x20;   "total\_amount":   { "value": 2783.00, "page\_number": 1 },

&#x20;   "line\_items": \[ { "description": "Office Chair", "quantity": 5, "unit\_price": 120, "amount": 600 } ]

&#x20; },

&#x20; "validation": {

&#x20;   "overall\_status": "PASS",

&#x20;   "checks": \[ { "name": "invoice\_total\_check", "formula": "subtotal + tax - discount",

&#x20;                 "calculated\_value": 2783.0, "reported\_value": 2783.0,

&#x20;                 "variance": 0.0, "status": "PASS" } ]

&#x20; },

&#x20; "processing\_metadata": { "ocr\_used": false, "llm\_used": true,

&#x20;                           "llm\_provider": "gemini", "llm\_model": "gemini-2.5-flash",

&#x20;                           "processed\_at": "2026-09-11T12:00:00Z",

&#x20;                           "processing\_time\_ms": 2840 }

}

Error response shape

json

{ "error": { "code": "UNSUPPORTED\_FILE\_TYPE",

&#x20;            "message": "Only PDF / JPG / PNG documents are supported." } }

7\. Financial validation rules

Rules are deterministic. Each check returns the formula used, operands,

calculated value, reported value, variance, and a status

(PASS / FAILED / NOT\_APPLICABLE).



Document	Check

Invoice	quantity × unit\_price ≈ line amount (per line)

Invoice	subtotal + tax\_amount − discount ≈ total\_amount

Invoice	sum(line\_items.amount) ≈ subtotal

Balance Sheet	total\_liabilities + total\_equity ≈ total\_assets

Balance Sheet	sum(asset components) ≈ reported total\_assets (per period)

P\&L	revenue − cost\_of\_sales ≈ gross\_profit

P\&L	gross\_profit − operating\_expenses ≈ operating\_profit

P\&L	operating\_profit − tax ≈ net\_profit

Cash Flow	operating + investing + financing ≈ net\_change\_in\_cash

Cash Flow	opening\_cash + net\_change\_in\_cash ≈ closing\_cash

Tolerance: max(0.01, 0.001 × |reported|). Parenthesized numbers (e.g. (1,234))

are treated as negative. Per-period checks run independently for each comparative year.



If a required operand is missing, the check returns NOT\_APPLICABLE — values are

never invented.



8\. Persistence

Model: backend/app/models/document.py (SQLAlchemy)



Repository: backend/app/repositories/document\_repository.py



Dev DB: SQLite (backend/documents.db)



Prod-ready: swap DATABASE\_URL to postgresql+psycopg2://... — same code path



Each processed document is stored as a row with:

document\_name, document\_type, processing\_status, overall\_confidence,

file\_validation (JSON), extracted\_data (JSON), validation (JSON),

processing\_metadata (JSON), created\_at.



GET /api/v1/documents/{name} returns the most recent row for that name.



9\. Testing

bash

cd backend

pytest -v

Covers:



File validation (type, size, page count, corrupted file)



Financial validation rules (invoice, balance sheet, P\&L, cash flow)



API flow (health, process, get-by-name, list)



10\. Sample outputs

See sample\_outputs/ for JSON responses from real documents:



invoice.json



balance\_sheet.json



profit\_and\_loss.json



cash\_flow\_statement.json



failure\_no\_text.json (documented NO\_TEXT\_EXTRACTED case)



11\. Known limitations

Free-tier deployment resets the DB on service sleep (Render). Use a

persistent Postgres or a paid instance for retention.



OCR quality depends on scan quality. Very low-DPI or skewed pages may

return NO\_TEXT\_EXTRACTED.



LLM extraction is best-effort. Occasionally a field is captured under a

synonym or missed; validation catches material inconsistencies.



Free-tier request timeout on Render is \~100s. Very large multi-page

documents may need a paid tier or async processing.



English-only OCR and prompt.



No authentication on the API — intended as a technical demonstration.



12\. Production improvements

Persistent Postgres + connection pooling (already DB-agnostic).



Async job queue (Celery / RQ) for documents > 2 pages; return 202 Accepted

with a job ID.



Object storage (S3) instead of ephemeral disk for original files.



Auth — API keys / OAuth2 + per-tenant rate limits.



Confidence scoring — combine OCR confidence + LLM logprobs into a

calibrated per-field score.



Redaction — PII stripping before external LLM calls.



Observability — OpenTelemetry traces, structured JSON logs, error tracking

(Sentry).



Schema versioning — version the response envelope for backward compatibility.



Golden test set with per-field precision/recall dashboards.



13\. AI / tool usage declaration

LLMs used in the product: Google Gemini (gemini-2.5-flash) for field and

table extraction with a strict JSON schema and page-level evidence.



AI coding assistants used during development:



Used for scaffolding, prompt iteration, and debugging (error triage,

Windows/PowerShell friction, Pydantic edge cases).



All financial validation logic is deterministic and hand-written; the LLM

is only used for structured extraction.



No sample outputs are hardcoded. Extraction runs live against uploaded files.



14\. Project structure

text

project-root/

├── backend/

│   ├── app/

│   │   ├── main.py

│   │   ├── api/routes/documents.py

│   │   ├── core/{config,database,logging}.py

│   │   ├── models/document.py

│   │   ├── schemas/{document,extraction}.py

│   │   ├── services/

│   │   │   ├── document\_validation\_service.py

│   │   │   ├── ocr\_service.py

│   │   │   ├── extraction\_service.py

│   │   │   ├── financial\_validation\_service.py

│   │   │   └── document\_service.py

│   │   ├── repositories/document\_repository.py

│   │   └── utils/

│   ├── tests/

│   └── requirements.txt

├── frontend/

│   ├── templates/{landing,dashboard,document\_result}.html

│   └── static/{css,js}/

├── docs/

│   └── architecture.png

├── sample\_outputs/

├── Dockerfile

├── .dockerignore

├── .env.example

├── .gitignore

└── README.md

15\. Author

Srishti Kumari

LinkedIn: https://www.linkedin.com/in/srishti-kumari-335b67252

GitHub: https://github.com/Srishtikumari510

