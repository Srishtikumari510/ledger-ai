# 🧾 LedgerAI

### AI-Powered Financial Document Intelligence, Validation & REST API Platform

<p align="center">

**Transform unstructured financial documents into structured, validated, and API-ready intelligence.**

</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge\&logo=fastapi\&logoColor=white)
![Gemini](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-4285F4?style=for-the-badge\&logo=google)
![Tesseract](https://img.shields.io/badge/OCR-Tesseract-5.x-555555?style=for-the-badge)
![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy-D71F00?style=for-the-badge\&logo=sqlalchemy\&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge\&logo=docker\&logoColor=white)
![Pytest](https://img.shields.io/badge/Tests-Pytest-0A9EDC?style=for-the-badge\&logo=pytest\&logoColor=white)

</p>

<p align="center">

[🚀 Live Demo](https://ledger-ai-y8ff.onrender.com/) •
[📊 Dashboard](https://ledger-ai-y8ff.onrender.com/dashboard) •
[📚 Swagger API](https://ledger-ai-y8ff.onrender.com/docs) •
[💻 GitHub](https://github.com/Srishtikumari510/ledger-ai)

</p>

---

## 📌 Project Overview

**LedgerAI** is an end-to-end **Intelligent Document Processing (IDP)** platform for financial documents.

It combines:

> **Document Validation → PDF Text Extraction → OCR → LLM Extraction → Structured JSON → Financial Validation → Database → REST API → Dashboard**

The system accepts:

* 📄 Invoices
* 📊 Balance Sheets
* 📈 Profit & Loss Statements
* 💰 Cash Flow Statements

in:

* PDF
* JPG
* PNG

Unlike a basic OCR system, LedgerAI does not stop after extracting text.

It uses **Google Gemini** to understand and structure financial information, then applies **deterministic financial rules** to independently verify the extracted values.

### Core principle

> **Use AI for understanding. Use deterministic software for correctness.**

This separation makes the system easier to reason about, test, debug, and extend.

---

# 🎯 Why LedgerAI?

Financial documents contain valuable information, but their data is frequently trapped inside:

* unstructured PDFs
* scanned documents
* inconsistent layouts
* financial tables
* different field naming conventions
* comparative financial statements

Traditional OCR can convert an image into text, but it does not understand the financial meaning of that text.

LedgerAI adds an intelligence layer:

```text
                 Raw Financial Document
                           │
                           ▼
                  Document Validation
                           │
                           ▼
                  Text Extraction / OCR
                           │
                           ▼
                AI Document Understanding
                           │
                           ▼
                    Structured JSON
                           │
                           ▼
                Financial Rule Engine
                           │
                           ▼
                 Validated Intelligence
                           │
                ┌──────────┴──────────┐
                ▼                     ▼
             Database              REST API
                                      │
                                      ▼
                                  Dashboard
```

---

# ✨ Key Features

## 📄 Multi-Document Financial Processing

LedgerAI currently supports four document categories:

| Document         | Example Validations                                 |
| ---------------- | --------------------------------------------------- |
| 🧾 Invoice       | Line amount, subtotal, tax, discount, total         |
| 📊 Balance Sheet | Assets = Liabilities + Equity                       |
| 📈 Profit & Loss | Revenue, gross profit, operating profit, net profit |
| 💰 Cash Flow     | Operating + Investing + Financing = Net Change      |

---

## 🔍 Intelligent Text Extraction

LedgerAI uses a layered extraction strategy.

### Native PDF

Machine-readable PDFs are processed using:

```text
PDF → pdfplumber → Extracted Text
```

### Scanned PDF / Images

When native text is unavailable:

```text
PDF/Image
   ↓
PDF → Image
   ↓
Tesseract OCR
   ↓
Extracted Text
```

This avoids unnecessary OCR processing when high-quality native PDF text is already available.

---

# 🤖 LLM-Powered Structured Extraction

Google Gemini is used for semantic document understanding.

The model extracts:

* financial fields
* document metadata
* line items
* financial tables
* comparative periods
* page-level evidence

The LLM output is constrained using structured schemas.

### Example

Instead of:

```text
Invoice Number: INV-2026-0042
Total: ₹2783
```

LedgerAI returns machine-readable data:

```json
{
  "invoice_number": {
    "value": "INV-2026-0042",
    "page_number": 1
  },
  "total_amount": {
    "value": 2783.00,
    "page_number": 1
  }
}
```

This allows the output to be directly consumed by:

* REST APIs
* databases
* analytics pipelines
* accounting systems
* downstream automation

---

# 🧮 Deterministic Financial Validation

This is one of the most important design decisions in LedgerAI.

The LLM **does not decide whether a financial calculation is correct**.

Instead:

```text
                 Gemini
                   │
                   │ Extract
                   ▼
             Structured Data
                   │
                   ▼
        Deterministic Rule Engine
                   │
          ┌────────┴────────┐
          ▼                 ▼
       Calculated         Reported
         Value              Value
          │                 │
          └────────┬────────┘
                   ▼
              Variance
                   │
                   ▼
          PASS / FAILED /
          NOT_APPLICABLE
```

### Invoice

```text
Quantity × Unit Price ≈ Line Amount

Subtotal + Tax − Discount ≈ Total

Σ Line Items ≈ Subtotal
```

### Balance Sheet

```text
Total Assets ≈ Total Liabilities + Total Equity
```

### Profit & Loss

```text
Revenue − Cost of Sales ≈ Gross Profit

Gross Profit − Operating Expenses ≈ Operating Profit

Operating Profit − Tax ≈ Net Profit
```

### Cash Flow

```text
Operating + Investing + Financing ≈ Net Change in Cash

Opening Cash + Net Change ≈ Closing Cash
```

### Missing Data

If a required operand is unavailable:

```text
NOT_APPLICABLE
```

The system does **not invent financial values**.

---

# 🏗️ System Architecture

```text
                         ┌─────────────────────┐
                         │       User          │
                         │   Browser / API     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      FastAPI        │
                         │   REST API Layer    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  Document Service   │
                         │    Orchestrator     │
                         └──────────┬──────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            │                       │                       │
            ▼                       ▼                       ▼
   ┌────────────────┐     ┌────────────────┐      ┌────────────────┐
   │ File Validation│     │ OCR / Text     │      │ Gemini LLM     │
   │                │     │ Extraction     │      │ Extraction     │
   └────────────────┘     └────────────────┘      └────────────────┘
            │                       │                       │
            └───────────────────────┼───────────────────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Financial Validation│
                         │   Rule Engine       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Repository Layer    │
                         │    SQLAlchemy       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ SQLite / PostgreSQL │
                         └──────────┬──────────┘
                                    │
                       ┌────────────┴────────────┐
                       ▼                         ▼
                ┌───────────────┐       ┌───────────────┐
                │   REST JSON   │       │ Jinja2        │
                │      API      │       │ Dashboard     │
                └───────────────┘       └───────────────┘
```

---

# 🔄 End-to-End Processing Flow

```text
1. Upload Document
        ↓
2. Validate File
        ↓
3. Detect Document Type
        ↓
4. Extract Native PDF Text
        ↓
5. If Required → OCR
        ↓
6. Send Structured Content to Gemini
        ↓
7. Extract Fields + Tables
        ↓
8. Attach Page-Level Evidence
        ↓
9. Run Financial Validation Rules
        ↓
10. Calculate Variance
        ↓
11. Persist Result
        ↓
12. Return Structured JSON
        ↓
13. Display Result on Dashboard
```

---

# 🧰 Technology Stack

| Layer         | Technology                  | Purpose                          |
| ------------- | --------------------------- | -------------------------------- |
| Backend       | **FastAPI**                 | REST API and application server  |
| Schemas       | **Pydantic v2**             | Request/response validation      |
| LLM           | **Google Gemini 2.5 Flash** | Financial document understanding |
| OCR           | **Tesseract 5.x**           | Scanned document text extraction |
| PDF           | **pdfplumber**              | Native PDF extraction            |
| PDF Rendering | **pdf2image + Poppler**     | Convert PDF pages for OCR        |
| ORM           | **SQLAlchemy**              | Database abstraction             |
| Database      | **SQLite**                  | Development persistence          |
| Production DB | **PostgreSQL-ready**        | Production persistence           |
| Frontend      | **Jinja2 + HTML/CSS/JS**    | Dashboard                        |
| Testing       | **Pytest**                  | Automated testing                |
| Deployment    | **Docker + Render**         | Containerized deployment         |
| API Docs      | **Swagger / OpenAPI**       | Interactive API documentation    |

---

# 📸 Screenshots & Demo

> Add your actual screenshots to `docs/screenshots/`.

Recommended structure:

```text
docs/
└── screenshots/
    ├── landing-page.png
    ├── upload-document.png
    ├── processing-result.png
    ├── validation-result.png
    ├── dashboard.png
    └── swagger-api.png
```

### 🏠 Landing Page

![LedgerAI Landing Page](docs/screenshots/landing-page.png)

---

### 📤 Document Upload

![Document Upload](docs/screenshots/upload-document.png)

---

### 🤖 AI Extraction Result

![Extraction Result](docs/screenshots/processing-result.png)

---

### 🧮 Financial Validation

![Financial Validation](docs/screenshots/validation-result.png)

---

### 📊 Dashboard

![LedgerAI Dashboard](docs/screenshots/dashboard.png)

---

### 📚 Swagger API

![Swagger API](docs/screenshots/swagger-api.png)

---

# 🌐 Live Demo

| Component       | Link                                              |
| --------------- | ------------------------------------------------- |
| 🚀 Landing Page | https://ledger-ai-y8ff.onrender.com/              |
| 📊 Dashboard    | https://ledger-ai-y8ff.onrender.com/dashboard     |
| 🔌 API Base     | https://ledger-ai-y8ff.onrender.com/api/v1        |
| ❤️ Health Check | https://ledger-ai-y8ff.onrender.com/api/v1/health |
| 📚 Swagger      | https://ledger-ai-y8ff.onrender.com/docs          |
| 💻 GitHub       | https://github.com/Srishtikumari510/ledger-ai     |

> **Deployment note:** The current Render free tier may sleep after inactivity. The first request after sleep can therefore take longer. SQLite storage is also ephemeral on the free tier.

---

# 🔌 REST API

LedgerAI exposes a versioned REST API:

```text
/api/v1
```

---

## 1️⃣ Process a Document

### Endpoint

```http
POST /api/v1/documents/process
```

### cURL

```bash
curl -X POST \
  "https://ledger-ai-y8ff.onrender.com/api/v1/documents/process" \
  -F "file=@sample_invoice.pdf" \
  -F "document_type=invoice"
```

### Supported Types

```text
invoice
balance_sheet
profit_and_loss
cash_flow_statement
```

---

## 2️⃣ Retrieve a Processed Document

```http
GET /api/v1/documents/{document_name}
```

Example:

```bash
curl \
"https://ledger-ai-y8ff.onrender.com/api/v1/documents/sample_invoice.pdf"
```

---

## 3️⃣ List Documents

```http
GET /api/v1/documents
```

Example:

```bash
curl \
"https://ledger-ai-y8ff.onrender.com/api/v1/documents"
```

---

## 4️⃣ Health Check

```http
GET /api/v1/health
```

Response:

```json
{
  "status": "ok",
  "service": "Document Intelligence API",
  "version": "1.0.0"
}
```

---

# 📦 Example API Response

```json
{
  "document_name": "sample_invoice.pdf",
  "document_type": "invoice",
  "processing_status": "PASS",

  "file_validation": {
    "file_type": "application/pdf",
    "page_count": 1,
    "status": "PASS"
  },

  "extracted_data": {
    "invoice_number": {
      "value": "INV-2026-0042",
      "page_number": 1
    },

    "total_amount": {
      "value": 2783.00,
      "page_number": 1
    },

    "line_items": [
      {
        "description": "Office Chair",
        "quantity": 5,
        "unit_price": 120,
        "amount": 600
      }
    ]
  },

  "validation": {
    "overall_status": "PASS",

    "checks": [
      {
        "name": "invoice_total_check",
        "formula": "subtotal + tax - discount",
        "calculated_value": 2783.0,
        "reported_value": 2783.0,
        "variance": 0.0,
        "status": "PASS"
      }
    ]
  },

  "processing_metadata": {
    "ocr_used": false,
    "llm_used": true,
    "llm_provider": "gemini",
    "llm_model": "gemini-2.5-flash",
    "processing_time_ms": 2840
  }
}
```

---

# ❌ Error Handling

Unsupported documents return structured errors.

Example:

```json
{
  "error": {
    "code": "UNSUPPORTED_FILE_TYPE",
    "message": "Only PDF / JPG / PNG documents are supported."
  }
}
```

This provides a predictable API contract for frontend and external clients.

---

# 🗄️ Persistence Architecture

LedgerAI uses SQLAlchemy as the persistence abstraction.

### Development

```text
SQLite
```

### Production

```text
PostgreSQL
```

The database URL can be changed through configuration without redesigning the repository layer.

Each processed document stores:

```text
document_name
document_type
processing_status
overall_confidence
file_validation
extracted_data
validation
processing_metadata
created_at
```

---

# 🧪 Testing

The project includes automated tests for:

### File Validation

* File type
* File size
* Page count
* Corrupted files

### Financial Validation

* Invoice rules
* Balance sheet rules
* P&L rules
* Cash flow rules

### API

* Health endpoint
* Document processing
* Document retrieval
* Document listing

Run:

```bash
cd backend
pytest -v
```

---

# 🛠️ Local Development

## Prerequisites

```text
Python 3.12
Tesseract OCR
Poppler
```

---

## Windows

Install external dependencies:

```powershell
winget install UB-Mannheim.TesseractOCR
winget install oschwartz10612.Poppler
```

Clone the repository:

```powershell
git clone https://github.com/Srishtikumari510/ledger-ai.git

cd ledger-ai/backend
```

Create virtual environment:

```powershell
py -3.12 -m venv venv

.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Configure environment variables:

```powershell
Copy-Item .env.example .env

notepad .env
```

Set:

```env
LLM_API_KEY=your_api_key
```

Run:

```powershell
uvicorn app.main:app --reload --port 8000
```

Open:

```text
Landing:
http://127.0.0.1:8000/

Dashboard:
http://127.0.0.1:8000/dashboard

Swagger:
http://127.0.0.1:8000/docs
```

---

# 🐳 Docker

Build:

```bash
docker build -t ledgerai .
```

Run:

```bash
docker run -p 8000:8000 --env-file .env ledgerai
```

The application can then be accessed at:

```text
http://localhost:8000
```

---

# 🔐 Environment Configuration

Example:

```env
APP_NAME=Document Intelligence API
APP_VERSION=1.0.0
LOG_LEVEL=INFO

DATABASE_URL=sqlite:///./documents.db

MAX_PAGES=3
MAX_FILE_SIZE_MB=20
UPLOAD_DIR=./uploads

LLM_PROVIDER=gemini
LLM_API_KEY=your_api_key_here
LLM_MODEL=gemini-2.5-flash

OCR_PROVIDER=tesseract
OCR_SPACE_API_KEY=
POPPLER_PATH=
```

Never commit:

```text
.env
```

to the repository.

---

# 📁 Project Structure

```text
ledger-ai/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── api/
│   │   │   └── routes/
│   │   │       └── documents.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── logging.py
│   │   │
│   │   ├── models/
│   │   │   └── document.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── document.py
│   │   │   └── extraction.py
│   │   │
│   │   ├── services/
│   │   │   ├── document_validation_service.py
│   │   │   ├── ocr_service.py
│   │   │   ├── extraction_service.py
│   │   │   ├── financial_validation_service.py
│   │   │   └── document_service.py
│   │   │
│   │   ├── repositories/
│   │   │   └── document_repository.py
│   │   │
│   │   └── utils/
│   │
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── templates/
│   │   ├── landing.html
│   │   ├── dashboard.html
│   │   └── document_result.html
│   │
│   └── static/
│       ├── css/
│       └── js/
│
├── docs/
│   ├── architecture.png
│   └── screenshots/
│
├── sample_outputs/
│   ├── invoice.json
│   ├── balance_sheet.json
│   ├── profit_and_loss.json
│   ├── cash_flow_statement.json
│   └── failure_no_text.json
│
├── Dockerfile
├── .dockerignore
├── .env.example
├── .gitignore
└── README.md
```

---

# 📊 Sample Outputs

The repository includes example JSON outputs for:

```text
invoice.json
balance_sheet.json
profit_and_loss.json
cash_flow_statement.json
failure_no_text.json
```

These demonstrate both successful processing and documented failure scenarios.

---

# ⚙️ Engineering Decisions

## Why FastAPI?

* Automatic OpenAPI documentation
* Pydantic integration
* High-performance API framework
* Clean route/service separation
* Easy local and containerized deployment

## Why Gemini?

* Structured JSON output
* Strong document understanding
* Low-latency extraction
* Suitable for the prototype's AI extraction layer

## Why Tesseract?

* Open-source
* Offline
* Mature OCR engine
* No mandatory external OCR API dependency

## Why Deterministic Validation?

LLMs are useful for interpreting documents but should not be trusted as the sole source of truth for arithmetic financial rules.

LedgerAI therefore separates:

```text
Semantic Intelligence
        ↓
       LLM

Financial Correctness
        ↓
Deterministic Rules
```

---

# 🧠 AI Engineering Principles

LedgerAI demonstrates several practical AI engineering patterns.

### 1. Structured LLM Output

LLM responses are constrained by schemas.

### 2. AI + Traditional Software

AI handles semantic interpretation while conventional code handles deterministic business logic.

### 3. Explainability

Validation responses expose:

```text
Formula
Operands
Calculated Value
Reported Value
Variance
Status
```

### 4. Graceful Failure

The system explicitly handles:

* unsupported file types
* corrupted documents
* missing text
* missing operands
* OCR failures
* extraction failures

### 5. Separation of Concerns

```text
API
 ↓
Service
 ↓
Extraction / Validation
 ↓
Repository
 ↓
Database
```

---

# 🚧 Known Limitations

The current deployment is intentionally a technical demonstration.

Known limitations include:

* OCR quality depends on scan quality.
* English-only OCR and prompts.
* LLM extraction is best-effort.
* Maximum document size/page count is limited.
* No API authentication currently.
* Render free-tier storage is ephemeral.
* Large documents may require asynchronous processing.

---

# 🔮 Production Roadmap

## Phase 1 — Infrastructure

* [ ] PostgreSQL
* [ ] Redis
* [ ] S3-compatible object storage
* [ ] Connection pooling

## Phase 2 — Scalability

* [ ] Celery/RQ job queue
* [ ] Asynchronous document processing
* [ ] `202 Accepted` + job ID
* [ ] Worker-based architecture

## Phase 3 — Security

* [ ] API keys
* [ ] OAuth2
* [ ] Per-tenant isolation
* [ ] Rate limiting
* [ ] PII redaction

## Phase 4 — AI Improvements

* [ ] Field-level confidence scoring
* [ ] OCR confidence integration
* [ ] Document classification
* [ ] Improved table extraction
* [ ] Human-in-the-loop verification
* [ ] Golden evaluation dataset

## Phase 5 — Observability

* [ ] OpenTelemetry
* [ ] Structured logs
* [ ] Sentry
* [ ] Processing latency metrics
* [ ] Extraction precision/recall dashboards

---

# 🏭 Production Architecture

The current synchronous prototype can evolve into:

```text
                    Client
                      │
                      ▼
                API Gateway
                      │
                      ▼
               FastAPI Backend
                      │
                      ▼
                Job Queue
              ┌───────┴───────┐
              ▼               ▼
         OCR Worker      LLM Worker
              │               │
              └───────┬───────┘
                      ▼
             Validation Engine
                      │
                      ▼
                PostgreSQL
                      │
             ┌────────┴────────┐
             ▼                 ▼
        Object Storage      Analytics
             │
             ▼
          Dashboard
```

This would allow LedgerAI to move from a demonstration platform toward a scalable document-processing service.

---

# 📈 What This Project Demonstrates

### AI / ML

* LLM integration
* Prompt engineering
* Structured extraction
* OCR pipelines
* Evidence-aware extraction

### Backend Engineering

* REST API design
* FastAPI
* Pydantic
* Service architecture
* Repository pattern
* Database persistence

### Data Engineering

* Structured JSON
* Financial data validation
* Schema-driven processing
* Comparative-period handling

### Software Engineering

* Modular architecture
* Automated testing
* Error handling
* Configuration management
* Docker deployment

### Production Thinking

* Authentication roadmap
* Async processing
* Object storage
* PostgreSQL migration
* Observability
* Confidence scoring
* Rate limiting

---

# ⭐ Recruiter Snapshot

| Capability                | Implementation                       |
| ------------------------- | ------------------------------------ |
| AI Document Understanding | Google Gemini                        |
| OCR                       | Tesseract                            |
| PDF Processing            | pdfplumber + pdf2image               |
| Backend                   | FastAPI                              |
| API Design                | REST + OpenAPI                       |
| Validation                | Pydantic + deterministic rule engine |
| Database                  | SQLAlchemy + SQLite                  |
| Production DB Path        | PostgreSQL                           |
| Frontend                  | Jinja2 + JavaScript                  |
| Testing                   | Pytest                               |
| Deployment                | Docker + Render                      |
| Architecture              | Layered service/repository design    |

---

# 💡 Core Takeaway

LedgerAI is not simply an OCR application and not simply an LLM wrapper.

It is an attempt to build a complete **AI-powered document intelligence system** where:

```text
           AI
           ↓
      Understand
           ↓
       Structure
           ↓
   Deterministic Logic
           ↓
       Validate
           ↓
        Persist
           ↓
          API
           ↓
       Application
```

> **AI extracts the meaning. Software verifies the numbers. APIs make the intelligence usable.**

---

# 👩‍💻 Author

## Srishti Kumari

**MCA Student | AI/ML & Software Engineering**

📌 Interested in:

* Artificial Intelligence
* Machine Learning
* LLM Applications
* Backend Engineering
* Intelligent Automation
* Data & Analytics

### Connect

* 💻 GitHub: https://github.com/Srishtikumari510
* 🔗 LinkedIn: https://www.linkedin.com/in/srishti-kumari-335b67252

---

# 🤖 AI / Tool Usage Disclosure

LedgerAI uses **Google Gemini 2.5 Flash** for field and table extraction using structured schemas and page-level evidence.

AI coding assistants were used during development for:

* scaffolding
* prompt iteration
* debugging
* error triage
* Pydantic edge cases
* Windows/PowerShell development issues

Financial validation logic is implemented using deterministic, hand-written rules.

The sample outputs are not hardcoded into the processing pipeline; extraction runs against uploaded documents.

---

<p align="center">

### 🚀 From Documents to Verified Financial Intelligence

**LedgerAI**

</p>
