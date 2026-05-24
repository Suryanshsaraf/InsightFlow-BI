<p align="center">
  <img src="docs/assets/logo.png" alt="InsightFlow Logo" width="80" height="80" />
</p>

<h1 align="center">InsightFlow</h1>

<p align="center">
  <strong>AI-Powered Business Intelligence for Everyone</strong>
</p>

<p align="center">
  Upload CSV → Instantly Understand Your Data
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#tech-stack">Tech Stack</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#api-reference">API Reference</a> •
  <a href="#contributing">Contributing</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.12+-blue.svg" alt="Python" />
  <img src="https://img.shields.io/badge/next.js-15-black.svg" alt="Next.js" />
  <img src="https://img.shields.io/badge/fastapi-0.115+-green.svg" alt="FastAPI" />
  <img src="https://img.shields.io/badge/postgresql-16-blue.svg" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/license-MIT-purple.svg" alt="License" />
</p>

---

## 🎯 What is InsightFlow?

InsightFlow is a **modern, AI-powered Business Intelligence platform** that transforms raw CSV data into actionable insights — instantly. Think of it as **PowerBI meets ChatGPT**, designed for non-technical users.

Upload any CSV file and InsightFlow will:
- 🤖 **Auto-generate dashboards** with the right chart types
- 📊 **Detect KPIs** and compute key metrics
- 🧠 **Generate AI insights** — trends, anomalies, correlations
- 💬 **Answer questions in plain English** via natural language → SQL
- 🔍 **Let you query data** with a built-in SQL editor

**No setup. No learning curve. No expensive licenses.**

---

## ✨ Features

### Core Features

| Feature | Description |
|---------|-------------|
| **📁 CSV Upload** | Drag-and-drop upload with validation, preview, and schema inference |
| **⚙️ Data Processing** | Automatic cleaning, type detection, and statistics computation |
| **📊 Auto Dashboards** | AI-selected chart types, KPI cards, and optimized layouts |
| **🔍 SQL Editor** | Full SQL query editor with syntax highlighting and autocomplete |
| **💬 Natural Language Queries** | Ask questions in English → get SQL + visualizations |
| **🧠 AI Insights** | GPT-powered trend analysis, anomaly detection, and recommendations |
| **🎨 Interactive Filtering** | Filter, sort, and drill into your data |
| **💾 Dashboard Persistence** | Save, reload, and manage your dashboards |
| **🔐 Authentication** | JWT-based auth with signup/login |
| **🌙 Dark Mode** | Beautiful dark and light themes |

### Dashboard Intelligence

InsightFlow's auto-dashboard engine analyzes your data columns and intelligently selects:

| Data Pattern | Chart Type |
|---|---|
| Date + Number | 📈 Line Chart |
| Category + Number | 📊 Bar Chart |
| Category (≤6 values) + Number | 🥧 Pie Chart |
| Number + Number | 🔵 Scatter Plot |
| Time Series (multiple) | 📊 Stacked Area |
| Any data | 📋 Data Table |

### AI-Generated Insights

InsightFlow uses OpenAI GPT-4o to automatically generate:
- 📈 **Trend Analysis** — growth rates, seasonal patterns
- 🚨 **Anomaly Detection** — outliers, unusual spikes
- 🔗 **Correlation Discovery** — relationships between variables
- 📝 **Executive Summaries** — natural language overview
- 💡 **Recommendations** — actionable next steps

---

## 🛠️ Tech Stack

### Frontend
| Technology | Purpose |
|---|---|
| [Next.js 15](https://nextjs.org/) | React framework with App Router |
| [TypeScript](https://www.typescriptlang.org/) | Type safety |
| [Tailwind CSS](https://tailwindcss.com/) | Utility-first styling |
| [Recharts](https://recharts.org/) | Data visualization |
| [react-grid-layout](https://github.com/react-grid-layout/react-grid-layout) | Dashboard grid |
| [Zustand](https://github.com/pmndrs/zustand) | State management |
| [TanStack Query](https://tanstack.com/query) | Server state & caching |
| [Framer Motion](https://www.framer.com/motion/) | Animations |
| [CodeMirror 6](https://codemirror.net/) | SQL editor |
| [Lucide React](https://lucide.dev/) | Icons |

### Backend
| Technology | Purpose |
|---|---|
| [FastAPI](https://fastapi.tiangolo.com/) | Async REST API framework |
| [SQLAlchemy 2.0](https://www.sqlalchemy.org/) | Async ORM |
| [PostgreSQL 16](https://www.postgresql.org/) | Primary database |
| [Redis](https://redis.io/) | Caching & task queue |
| [Pandas](https://pandas.pydata.org/) | Data processing |
| [OpenAI API](https://platform.openai.com/) | AI insights & NL-to-SQL |
| [Alembic](https://alembic.sqlalchemy.org/) | Database migrations |
| [ARQ](https://arq-docs.helpmanual.io/) | Async background tasks |

### Infrastructure
| Technology | Purpose |
|---|---|
| [Docker](https://www.docker.com/) | Containerization |
| [Vercel](https://vercel.com/) | Frontend hosting |
| [Render](https://render.com/) / [Railway](https://railway.app/) | Backend hosting |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+**
- **Node.js 20+**
- **PostgreSQL 16** (or Docker)
- **Redis** (or Docker)
- **OpenAI API Key** (for AI features)

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/Suryanshsaraf/InsightFlow-BI.git
cd InsightFlow-BI

# Copy environment files
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local

# Edit .env and add your OpenAI API key
nano .env

# Start all services
docker compose up -d

# The app will be available at:
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup

#### Backend

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your database URL and OpenAI key

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Copy and configure environment
cp .env.local.example .env.local

# Start development server
npm run dev
```

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Client Layer                          │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Next.js Frontend                    │   │
│  │   Landing • Dashboards • Upload • SQL • Auth     │   │
│  └─────────────────────┬───────────────────────────┘   │
│                        │ HTTPS                          │
├────────────────────────┼────────────────────────────────┤
│                  API Gateway                             │
│                        │                                 │
│  ┌─────────────────────┴───────────────────────────┐   │
│  │              FastAPI Backend                      │   │
│  │   REST API • JWT Auth • WebSocket                 │   │
│  └──┬──────┬──────┬──────┬──────┬─────────────────┘   │
│     │      │      │      │      │                       │
├─────┼──────┼──────┼──────┼──────┼───────────────────────┤
│     │  Processing Layer  │      │                       │
│     │      │      │      │      │                       │
│  ┌──┴──┐┌──┴──┐┌──┴──┐┌──┴──┐┌──┴──┐                  │
│  │ CSV ││Chart││ KPI ││ SQL ││ AI  │                  │
│  │Proc.││Rec. ││Det. ││Eng. ││Eng. │                  │
│  └──┬──┘└──┬──┘└──┬──┘└──┬──┘└──┬──┘                  │
│     │      │      │      │      │                       │
├─────┼──────┼──────┼──────┼──────┼───────────────────────┤
│     │      Data Layer    │      │                       │
│     │      │      │      │      │                       │
│  ┌──┴──────┴──────┴──────┴──┐┌──┴──┐                   │
│  │     PostgreSQL           ││Redis│                   │
│  │  (App Data + User Data)  ││Cache│                   │
│  └──────────────────────────┘└─────┘                   │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

```
CSV Upload → Validate → Stream to Disk → Background Process
                                              │
                        ┌─────────────────────┤
                        │                     │
                   Clean Data           Infer Types
                        │                     │
                        └──────┬──────────────┘
                               │
                    Create SQL Table (user_data schema)
                               │
                    Compute Column Statistics
                               │
                    ┌──────────┴──────────┐
                    │                     │
              Generate KPIs      Recommend Charts
                    │                     │
                    └──────────┬──────────┘
                               │
                    Create Dashboard Config
                               │
                    Generate AI Insights (async)
                               │
                    Return Dashboard to User
```

### Database Schema

```
users ──┬── datasets ──┬── dataset_columns
        │              ├── dashboards ──┬── charts
        │              │                ├── kpis
        │              │                └── insights
        └── query_history
```

### Folder Structure

```
InsightFlow-BI/
├── frontend/               # Next.js 15 application
│   ├── src/
│   │   ├── app/           # App Router pages
│   │   ├── components/    # React components
│   │   │   ├── ui/        # Base UI primitives
│   │   │   ├── layout/    # Layout components
│   │   │   ├── dashboard/ # Dashboard components
│   │   │   ├── charts/    # Chart components
│   │   │   ├── dataset/   # Dataset components
│   │   │   ├── query/     # SQL query components
│   │   │   └── shared/    # Shared components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── stores/        # Zustand stores
│   │   ├── lib/           # Utilities
│   │   └── types/         # TypeScript types
│   └── public/
│
├── backend/                # FastAPI application
│   ├── app/
│   │   ├── api/v1/        # API routes
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   ├── core/          # Security, middleware
│   │   ├── tasks/         # Background tasks
│   │   └── utils/         # Helpers
│   ├── alembic/           # DB migrations
│   └── tests/
│
├── docker-compose.yml
├── docker-compose.dev.yml
└── docs/
```

---

## 📡 API Reference

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/signup` | Create account |
| `POST` | `/api/v1/auth/login` | Login (returns JWT) |
| `POST` | `/api/v1/auth/refresh` | Refresh access token |
| `GET` | `/api/v1/auth/me` | Get current user |

### Datasets

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/datasets/upload` | Upload CSV file |
| `GET` | `/api/v1/datasets/` | List datasets |
| `GET` | `/api/v1/datasets/{id}` | Get dataset details |
| `GET` | `/api/v1/datasets/{id}/preview` | Preview data (first 100 rows) |
| `GET` | `/api/v1/datasets/{id}/stats` | Get column statistics |
| `DELETE` | `/api/v1/datasets/{id}` | Delete dataset |

### Dashboards

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/dashboards/generate` | Auto-generate dashboard |
| `GET` | `/api/v1/dashboards/` | List dashboards |
| `GET` | `/api/v1/dashboards/{id}` | Get dashboard with charts |
| `PUT` | `/api/v1/dashboards/{id}` | Update dashboard |
| `DELETE` | `/api/v1/dashboards/{id}` | Delete dashboard |

### SQL Queries

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/queries/execute` | Execute SQL query |
| `POST` | `/api/v1/queries/natural-language` | NL → SQL → Results |
| `GET` | `/api/v1/queries/history` | Query history |

### AI Insights

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/insights/generate` | Generate AI insights |
| `GET` | `/api/v1/insights/dashboard/{id}` | Get dashboard insights |

> 📖 Full interactive API docs available at `http://localhost:8000/docs` when running locally.

---

## 🔧 Configuration

### Environment Variables

#### Backend (`backend/.env`)

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://...` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `SECRET_KEY` | JWT signing key | — (required) |
| `OPENAI_API_KEY` | OpenAI API key | — (required for AI) |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |
| `UPLOAD_DIR` | File upload directory | `/data/uploads` |
| `MAX_FILE_SIZE_MB` | Max upload size | `100` |

#### Frontend (`frontend/.env.local`)

| Variable | Description | Default |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |
| `NEXT_PUBLIC_APP_NAME` | App display name | `InsightFlow` |

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest tests/ -v --cov=app
```

### Frontend Tests

```bash
cd frontend
npm run test
```

---

## 📈 Roadmap

### MVP (Current)
- [x] CSV upload & processing
- [x] Auto-dashboard generation
- [x] KPI detection
- [x] Interactive charts
- [x] SQL query editor
- [x] Natural language queries
- [x] AI insights
- [x] JWT authentication
- [x] Dark mode

### v1.1 — Enhanced Analytics
- [ ] Multiple CSV joins
- [ ] Scheduled data refresh
- [ ] Custom chart builder
- [ ] Dashboard templates
- [ ] Export to PDF/PNG

### v1.2 — Collaboration
- [ ] Team workspaces
- [ ] Shared dashboards
- [ ] Comments & annotations
- [ ] Role-based access control

### v2.0 — Enterprise
- [ ] Real-time data connectors (PostgreSQL, MySQL, APIs)
- [ ] Predictive analytics & forecasting
- [ ] Embedded analytics (iframe/SDK)
- [ ] White-labeling
- [ ] SSO (SAML, OIDC)

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — New feature
- `fix:` — Bug fix
- `refactor:` — Code refactoring
- `docs:` — Documentation
- `test:` — Tests
- `chore:` — Maintenance

### Code Style

- **Python**: Black (line length: 100), Ruff linter, Google-style docstrings
- **TypeScript**: Prettier, ESLint with Next.js config

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) — Awesome Python web framework
- [Next.js](https://nextjs.org/) — The React framework
- [Recharts](https://recharts.org/) — React charting library
- [OpenAI](https://openai.com/) — AI-powered insights
- [Tailwind CSS](https://tailwindcss.com/) — Utility-first CSS

---

<p align="center">
  Built with ❤️ by the InsightFlow team
</p>
