# Deployment Plan: Spotify Growth Discovery Engine

This document outlines the deployment strategy, target environments, variables, and security boundaries for the prototype system.

---

## 1. Prototype and Workflow Access Links

*   **Test Workflow Link (Visual Pipeline/Runner):** 
    - `https://n8n.spotify-discovery-engine.cloud/workflow/1` (Self-hosted/Cloud workflow runner canvas containing the prompt chains, scrapers, and database nodes)
*   **Deployed Prototype Dashboard Link:** 
    - `https://spotify-discovery-engine.vercel.app` (Live React-based dashboard interface for product managers to query reviews and analyze weekly AI recommendations)

---

## 2. Preferred Hosting Stack

| Component | Target Platform | Justification |
| :--- | :--- | :--- |
| **Frontend** | **Vercel** | Zero-configuration static hosting, fast globally distributed Edge CDN, automatic Git integration. |
| **Backend API** | **Render (Web Service)** | Simple containerized or Node.js deployment, automated SSL, direct logs, free/low-cost tiers. |
| **Database** | **Supabase / Neon** | Fully managed serverless PostgreSQL database with immediate connection pooling and indexing support. |
| **Workflow Engine**| **Render (Docker Node) / n8n Cloud** | Run n8n or custom flow scripts in isolated environments with built-in cron schedulers. |

---

## 3. Environment Variables

### Frontend Environment (`.env.production`)
```bash
# Target backend API root endpoint
VITE_API_BASE_URL=https://spotify-discovery-api.onrender.com/api/v1
```

### Backend Environment (`.env`)
```bash
# Server Port Configuration
PORT=8080

# Database Access Connection
DATABASE_URL=postgresql://db_user:db_password@ep-cool-waterfall-123456.us-east-2.aws.neon.tech/spotify_feedback?sslmode=require

# AI Services
OPENAI_API_KEY=sk-proj-abcdefghijklmnopqrstuvwxyz1234567890

# Scraper Credentials
REDDIT_CLIENT_ID=reddit_client_abc123
REDDIT_CLIENT_SECRET=reddit_secret_xyz789

# Workflow Hook URL
WORKFLOW_ENGINE_URL=https://n8n.spotify-discovery-engine.cloud/webhook/trigger-pipeline

# CORS Configurations
CORS_ORIGIN=https://spotify-discovery-engine.vercel.app
```

---

## 4. Secret Storage Management

*   **Local Development:** Secrets are kept strictly in a local `.env` file at the repository root. This file is explicitly listed in `.gitignore` and is never committed to GitHub.
*   **Production Server Environments:**
    *   *Vercel:* Set in **Vercel Project Settings > Environment Variables** (values are encrypted at rest by Vercel).
    *   *Render:* Defined in the **Render Web Service Settings > Environment Variables** dashboard (or as a private Secret File).

---

## 5. Security & Visibility Boundaries

### What Must Be Public
*   **Frontend Dashboard UI:** The compiled static web bundle (`index.html`, javascript files, and stylesheets) must be served publicly so stakeholder groups can view the prototype.
*   **Backend Client API Endpoints:** Standard REST paths serving filtered query data to the dashboard (secured with basic API keys or session cookies if authentication is enabled):
    *   `GET /api/v1/reviews`
    *   `GET /api/v1/insights/summary`
    *   `GET /api/v1/insights/export`

### What Must Stay Private
*   **Database Credentials (`DATABASE_URL`):** Kept inside the secure backend host. Direct SQL ports should be IP-restricted to backend server instances only.
*   **LLM Provider API Keys (`OPENAI_API_KEY`):** Must never leak to the client frontend bundle to prevent key theft and billing abuse.
*   **Pipeline Scraper Keys:** Authentication credentials for Reddit, Play Store, and App Store endpoints.
*   **Internal Workflow Webhook Keys:** Secret tokens validating webhook ingestion requests, ensuring external bad actors cannot trigger massive analysis loops or inject false review reports.
