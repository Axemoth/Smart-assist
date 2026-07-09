<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white" />
  <img src="https://img.shields.io/badge/DeepSeek_AI-5B21B6?style=for-the-badge&logo=openai&logoColor=white" />
  <img src="https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white" />
</p>

# 🧠 Smart Assist

> **Intelligent workflow optimization and task scheduling — powered by AI.**

Smart Assist is a full-stack AI-powered task management application built with **FastAPI**, **PostgreSQL**, **Redis**, and **DeepSeek AI**. It features JWT authentication, email verification, intelligent task parsing, and a sleek glassmorphic neon-green UI.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 **JWT Authentication** | Secure access & refresh token flow with automatic rotation |
| 📧 **Email Verification** | Account verification via signed email links (Resend SMTP) |
| 🤖 **AI-Powered Tasks** | Natural language task parsing, smart rewriting & checklist breakdown via DeepSeek |
| 🔒 **Account Lockout** | Redis-backed brute-force protection (5 failed attempts → 10 min lock) |
| ⚡ **Rate Limiting** | Token Bucket algorithm to prevent API abuse per client IP |
| 🎯 **Task Priorities** | High / Medium / Low priority levels with color-coded UI |
| 🌐 **Serverless Deploy** | Production-ready on Vercel with Neon PostgreSQL & Upstash Redis |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI, SQLAlchemy, Pydantic v2 |
| **Database** | PostgreSQL (Neon) / SQLite (local dev) |
| **Cache** | Redis (Upstash) |
| **AI** | DeepSeek v4 Pro (OpenAI-compatible API) |
| **Auth** | JWT (PyJWT), Argon2 password hashing |
| **Email** | FastAPI-Mail + Resend SMTP |
| **Frontend** | Vanilla HTML/CSS/JS — Glassmorphic dark theme |
| **Deployment** | Vercel Serverless Functions |

---

## 📁 Project Structure

```
smart-assist/
├── api/
│   └── index.py              # Vercel serverless entrypoint
├── app/
│   ├── api/
│   │   ├── auth.py            # Register, verify, login, logout
│   │   ├── tasks.py           # CRUD + AI endpoints for tasks
│   │   └── users.py           # User profile & admin endpoints
│   ├── core/
│   │   ├── config.py          # Pydantic Settings (env vars)
│   │   ├── dependencies.py    # DI: get_db, get_current_user
│   │   └── security.py        # Password hashing, JWT creation
│   ├── db/
│   │   ├── base.py            # SQLAlchemy declarative base
│   │   └── session.py         # Engine & session factory
│   ├── error/                 # Custom exception handlers
│   ├── models/
│   │   ├── task_model.py      # Task ORM model
│   │   └── user_model.py      # User + RefreshToken ORM models
│   ├── repositories/          # Database query layer
│   ├── schemas/               # Pydantic request/response schemas
│   ├── services/
│   │   └── ai_service.py      # DeepSeek AI integration
│   └── utlis/
│       ├── cache.py           # Redis client + lockout helpers
│       ├── rate_limiter.py    # Token Bucket middleware
│       └── mail_utils/        # Email config + templates
├── static/
│   ├── index.html             # SPA frontend
│   ├── style.css              # Glassmorphic neon theme
│   └── app.js                 # Frontend logic
├── vercel.json                # Vercel deployment config
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker support for local dev
└── .env.example               # Environment variable template
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Docker (optional, for containerized dev)
- PostgreSQL or SQLite
- Redis

### Local Development

```bash
# Clone the repo
git clone https://github.com/Axemoth/Smart-assist.git
cd Smart-assist

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run the server
uvicorn app.main:app --reload --port 8000
```

### Docker

```bash
docker build -t smart-assist .
docker run -p 8000:8000 --env-file .env --name smart-assist smart-assist
```

Visit **http://localhost:8000** 🎉

---

## ⚙️ Environment Variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require

# Auth
ACCESS_SECRET_KEY=your-access-secret
REFRESH_SECRET_KEY=your-refresh-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_URL=rediss://default:token@host:6379

# Email (Resend)
MAIL_USERNAME=resend
MAIL_PASSWORD=re_your_api_key
MAIL_FROM=noreply@yourdomain.com
MAIL_PORT=465
MAIL_SERVER=smtp.resend.com
MAIL_FROM_NAME="Smart Assist"
MAIL_STARTTLS=False
MAIL_SSL_TLS=True
USE_CREDENTIALS=True
VALIDATE_CERTS=True

# Domain
DOMAIN=yourdomain.com

# AI
DEEPSEEK_API_KEY=sk-your-deepseek-key
DEEPSEEK_MODEL=deepseek-v4-pro
```

---

## 🗄️ Database Schema

<img src="jwt-authentication-erd.png" alt="Entity Relationship Diagram" width="550"/>

| Table | Description |
|-------|-------------|
| **Users** | User accounts with email, hashed password, role, verification status |
| **Tasks** | Tasks with title, description, status, priority, linked to user via FK |
| **RefreshTokens** | Stored refresh tokens with expiry, linked to user via FK |

---

## 🔑 API Endpoints

### Auth (`/auth`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Register a new account |
| `GET` | `/auth/verify/{token}` | Verify email address |
| `POST` | `/auth/login` | Login (returns access + refresh tokens) |
| `POST` | `/auth/logout` | Logout (invalidates refresh token) |

### Tasks (`/tasks`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/tasks/` | Get all tasks for current user |
| `POST` | `/tasks/` | Create a new task |
| `PUT` | `/tasks/{id}` | Update a task |
| `DELETE` | `/tasks/{id}` | Delete a task |
| `POST` | `/tasks/ai/parse` | 🤖 Parse natural language into a task |
| `POST` | `/tasks/ai/rewrite/{id}` | 🤖 AI rewrite task title & description |
| `POST` | `/tasks/ai/checklist/{id}` | 🤖 AI breakdown into checklist |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/me` | Get current user profile |
| `GET` | `/users` | Get all users (admin only) |

---

## 🛡️ Security Features

### 🔄 Refresh Token Rotation
Refresh tokens are stored in the database. On each refresh, the old token is invalidated and a new pair (access + refresh) is issued — preventing token reuse attacks.

### 🔒 Account Lockout
Failed login attempts are tracked in Redis. After **5 consecutive failures**, the account is locked for **10 minutes**. The counter resets on successful login.

### ⚡ Rate Limiting (Token Bucket)
Each client IP gets a bucket of **10 tokens**, refilling at **1 token/second**. Requests consume 1 token each. When depleted, the API returns `429 Too Many Requests` until tokens refill.

---

## 🤖 AI Integration

Smart Assist uses **DeepSeek v4 Pro** (OpenAI-compatible) for three AI features:

- **Parse** — Type a sentence like *"Buy groceries tomorrow high priority"* and the AI extracts a structured task with title, description, due date, and priority.
- **Rewrite** — Select any task and let AI improve its title and description for clarity.
- **Checklist** — Break a complex task into actionable sub-steps automatically.

All AI calls use JSON mode for reliable structured output, with a mock fallback when no API key is configured.

---

## 🌐 Deployment (Vercel)

This project is production-deployed on **Vercel** with:
- **Neon** — Serverless PostgreSQL
- **Upstash** — Serverless Redis
- **Resend** — Transactional email

```bash
# Push to GitHub triggers auto-deploy
git push origin main
```

Add all `.env` variables to **Vercel → Project → Settings → Environment Variables**.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  Built with 💚 by <a href="https://github.com/Axemoth">Axemoth</a>
</p>
