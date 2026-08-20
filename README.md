# FinSight

### Financial Data Analytics & AI Platform

FinSight is a full-stack financial analytics platform designed to transform raw financial data into validated, structured, and actionable insights.

It combines a production-style **ETL pipeline**, **data-quality validation**, **financial analytics**, **REST APIs**, **PostgreSQL**, an interactive **React dashboard**, and an **AI-powered financial analyst** into a single platform.

---

## ✨ Overview

Financial datasets often contain missing values, inconsistent records, invalid financial relationships, and other quality issues that can affect downstream analysis.

FinSight addresses this problem by introducing a structured data-processing workflow:

```text
                    ┌─────────────────────┐
                    │   Raw Financial     │
                    │       Data          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      Ingestion      │
                    │   CSV Processing    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Schema Validation   │
                    │ + Financial Rules   │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
          ┌──────────────────┐   ┌──────────────────┐
          │ Valid Records    │   │ Rejected Records │
          └────────┬─────────┘   └──────────────────┘
                   │
                   ▼
          ┌──────────────────────┐
          │ Data Quality Metrics │
          │ Completeness         │
          │ Validity             │
          │ Uniqueness           │
          │ Consistency          │
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ Financial Analytics  │
          │ Company Metrics      │
          │ Rankings             │
          │ Industry Benchmarks  │
          └──────────┬───────────┘
                     │
             ┌───────┴────────┐
             ▼                ▼
     ┌───────────────┐  ┌────────────────┐
     │ React         │  │ AI Financial   │
     │ Dashboard     │  │ Analyst        │
     └───────────────┘  └────────────────┘
The platform also maintains pipeline execution history and monitoring information, making the ETL process observable rather than treating it as a black box.

🚀 Key Features
📥 Financial Data Ingestion
CSV-based financial data ingestion
Structured input validation
Configurable source and output paths
Processed and rejected record separation
🔍 Data Validation

FinSight validates financial datasets at multiple levels:

Schema validation
Required-column validation
Data-type validation
Financial business-rule validation
Invalid-record detection

Invalid records are separated from valid records instead of silently entering downstream analytics.

📊 Data Quality Assessment

Each pipeline execution generates quality metrics including:

Completeness
Validity
Uniqueness
Consistency
Overall Quality Score

This provides visibility into the reliability of the dataset being processed.

⚙️ ETL Pipeline

The pipeline follows a structured workflow:

Extract
   ↓
Schema Validation
   ↓
Financial Rule Validation
   ↓
Quality Assessment
   ↓
Transform / Process
   ↓
Write Valid Records
   ↓
Write Rejected Records
   ↓
Track Pipeline Run

Pipeline executions record:

Run ID
Pipeline name
Execution status
Start time
Completion time
Records extracted
Records processed
Records rejected
Error information
📈 Financial Analytics

FinSight provides analytical capabilities for:

Company financial metrics
Company rankings
Revenue analysis
Profitability analysis
Return on assets
Debt ratios
Operating cash flow
Industry benchmarking
Historical financial periods
🏢 Company Analysis

Company-level views provide financial information across available reporting periods, allowing users to examine:

Revenue
Net income
Profit margins
ROA
Debt ratios
Operating cash flow
Financial trends
🏭 Industry Benchmarking

Companies can be analyzed relative to their industries using aggregated metrics such as:

Average revenue
Average net profit margin
Average operating margin
Average debt-to-assets
Average ROA
Average operating cash-flow margin
Company count
🤖 AI Financial Analyst

FinSight integrates an AI analyst capable of answering financial questions using structured company and portfolio context.

The system supports:

Single-company analysis
Portfolio-level analysis
Company comparison
Natural-language financial questions

The AI layer is integrated into the application rather than functioning as a standalone chatbot.

📡 Pipeline Monitoring

The monitoring interface provides operational visibility into:

Total pipeline runs
Successful runs
Failed runs
Success rate
Records extracted
Records processed
Records rejected
Latest successful execution
Latest failed execution
Recent pipeline history
🖥️ Interactive Dashboard

The React frontend provides dedicated interfaces for:

Dashboard
Companies
Company details
Rankings
Industries
AI Analyst
Pipeline operations
Monitoring

The UI is designed around financial analytics and operational visibility rather than exposing raw API responses directly to users.

🏗️ Architecture

FinSight follows a layered architecture.

┌─────────────────────────────────────────────┐
│                 React UI                    │
│             TypeScript + Vite               │
└──────────────────────┬──────────────────────┘
                       │ REST API
                       ▼
┌─────────────────────────────────────────────┐
│                FastAPI                      │
│              API Layer                      │
├─────────────────────────────────────────────┤
│ Analytics │ Pipeline │ Monitoring │ AI      │
└──────────────────────┬──────────────────────┘
                       │
          ┌────────────┴─────────────┐
          ▼                          ▼
┌─────────────────────┐    ┌──────────────────┐
│   ETL / Validation  │    │   PostgreSQL     │
│                     │    │                  │
│ Ingestion           │    │ Financial Data   │
│ Schema Validation   │    │ Analytics Data   │
│ Financial Rules     │    │ Application Data │
│ Quality Metrics     │    │                  │
└──────────┬──────────┘    └──────────────────┘
           │
           ▼
┌─────────────────────┐
│     Raw / Processed │
│     / Rejected Data │
└─────────────────────┘
🛠️ Technology Stack
Backend
Technology	Purpose
Python	Core backend and data processing
FastAPI	REST API framework
Pydantic	Request/response validation
Pandas	Financial data processing
PostgreSQL	Relational database
Pytest	Automated testing
Frontend
Technology	Purpose
React	UI framework
TypeScript	Type-safe frontend development
Vite	Frontend tooling and build system
CSS	Application styling
Lucide React	UI icons
AI
Technology	Purpose
Ollama	Local LLM runtime
Llama	Financial analysis and natural-language responses
Infrastructure
Technology	Purpose
Docker	Application containerization
Docker Compose	Multi-container development environment
PostgreSQL Container	Local database service
📁 Project Structure
finsight/
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── rejected/
│   └── monitoring/
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── pages/
│   │   ├── types/
│   │   ├── App.tsx
│   │   └── App.css
│   ├── package.json
│   └── vite.config.*
│
├── src/
│   └── finsight/
│       ├── ai/
│       ├── analytics/
│       ├── api/
│       ├── config/
│       ├── database/
│       ├── ingestion/
│       ├── pipeline/
│       ├── quality/
│       └── validation/
│
├── tests/
│   ├── api/
│   ├── analytics/
│   ├── ingestion/
│   ├── pipeline/
│   ├── quality/
│   └── validation/
│
├── docker-compose.yml
├── pyproject.toml
├── .env.example
└── README.md
⚡ Getting Started
Prerequisites

Make sure the following are installed:

Python 3.11+
Node.js
npm
Docker
Docker Compose
Git

For the AI analyst, Ollama should also be installed and configured locally.

1. Clone the Repository
git clone <your-repository-url>
cd finsight
2. Configure Environment Variables

Create a local environment file:

cp .env.example .env

Update the values in .env according to your local environment.

.env contains local configuration and should not be committed to Git.

🐳 Running with Docker

Start the backend and PostgreSQL:

docker compose up --build

The API will be available at:

http://localhost:8000

PostgreSQL is exposed locally through the configured Docker port.

To check running containers:

docker compose ps

To view API logs:

docker compose logs api
🎨 Running the Frontend

Open another terminal:

cd frontend
npm install
npm run dev

The Vite development server will provide the frontend URL in the terminal.

For a production build:

npm run build
🧪 Running Tests

FinSight includes an automated backend test suite covering API, analytics, ingestion, pipeline, quality, and validation functionality.

Run:

pytest -q

Current project checkpoint:

218 tests passed

This provides automated regression coverage across the core application.

🔄 Running the ETL Pipeline

The pipeline can be triggered through the API.

curl -X POST http://localhost:8000/api/pipeline/run

Pipeline status:

curl http://localhost:8000/api/pipeline/status

Monitoring information:

curl http://localhost:8000/api/monitoring

A successful pipeline execution records the run and reports:

Records extracted
Records processed
Records rejected
Completeness
Validity
Uniqueness
Consistency
Overall quality
📊 Example Pipeline Result

A typical successful execution follows this pattern:

Financial Dataset
       │
       ▼
   20,000 records
       │
       ▼
Schema Validation
       │
       ▼
Financial Rules
       │
       ├──────────────► Rejected: 7
       │
       ▼
Valid Records: 19,993
       │
       ▼
Quality Assessment
       │
       ▼
Processed Dataset

The exact results depend on the input dataset.

🔌 API Overview

The backend exposes REST endpoints for the major application capabilities.

Health / Readiness
GET /api/health
GET /api/readiness
Companies
GET /api/companies/{company_id}/summary
GET /api/companies/{company_id}/metrics
Rankings
GET /api/rankings
GET /api/companies/rankings
Industry Analytics
GET /api/industries/benchmarks
Pipeline
GET  /api/pipeline/status
POST /api/pipeline/run
Monitoring
GET /api/monitoring
AI Analysis

FinSight also exposes endpoints for:

Company analysis
Portfolio analysis
Company comparison

The exact request and response schemas are defined by the FastAPI application.

🔐 Data Quality Philosophy

A key design principle of FinSight is:

Bad data should be visible, not silently discarded.

Instead of simply removing invalid records, the pipeline separates them into rejected outputs and tracks the rejection count as part of the pipeline execution.

This makes it possible to answer:

How much data entered the pipeline?
How much was valid?
How much was rejected?
Why should the resulting analytics be trusted?
What was the quality of the dataset during a particular run?
🧠 AI Architecture

The AI analyst does not operate independently of the financial data layer.

The application first constructs relevant financial context and then passes that context to the local LLM.

Conceptually:

User Question
      │
      ▼
FastAPI
      │
      ▼
Financial Context Builder
      │
      ├── Company Metrics
      ├── Historical Data
      ├── Rankings
      └── Portfolio Context
      │
      ▼
Local LLM
      │
      ▼
Financial Explanation
      │
      ▼
React UI

This approach helps keep the AI analysis grounded in the application's structured financial data.

📈 Why FinSight?

FinSight was designed around a simple idea:

Financial analytics is only as reliable as the data-processing pipeline behind it.

Rather than building only a dashboard, the project combines:

Data Engineering
       +
Data Quality
       +
Financial Analytics
       +
Backend APIs
       +
Interactive Frontend
       +
AI

This makes the system representative of a complete data-driven application rather than an isolated visualization project.

🧪 Testing Strategy

The project uses automated tests to validate the core layers of the system.

Testing covers areas including:

API behavior
Validation rules
Financial calculations
Data ingestion
Pipeline execution
Quality metrics
Analytics services
Error handling

The current test suite contains:

218 passing tests

🚧 Known Limitations

FinSight is primarily a placement-oriented engineering project and is not intended to be presented as a production financial product.

Current limitations include:

Financial data is dependent on the supplied dataset.
AI responses depend on the locally configured LLM.
Authentication and authorization are not implemented as a production identity system.
Deployment infrastructure is designed primarily for local development.
The project does not provide investment advice or real-time market data.
🔮 Future Improvements

Potential future extensions include:

Cloud deployment
Authentication and role-based access control
Scheduled ETL execution
Real-time financial data ingestion
Advanced portfolio analytics
More sophisticated anomaly detection
Distributed data processing
CI/CD automation
Production observability
Advanced financial forecasting
Model evaluation and AI response monitoring
🎯 Project Goals

FinSight was built to demonstrate practical understanding of:

Full-stack application development
REST API design
Data engineering
ETL pipeline architecture
Data validation
Data quality engineering
SQL and relational databases
Financial analytics
AI integration
Containerization
Automated testing
Frontend development
