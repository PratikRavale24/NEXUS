# NEXUS

NEXUS is an explainable criminal-network intelligence prototype for authorized analysis. It combines entity resolution, temporal relationships, graph exploration, anomaly candidates, evidence provenance, investigator review, and a CCTNS-inspired case/FIR workspace.

All bundled records are deterministic synthetic demonstration data. Graph and anomaly outputs are analytical leads, not determinations of guilt.

## Architecture

- **Frontend:** Next.js, React, TypeScript, Tailwind CSS, Cytoscape.js
- **API:** FastAPI and Pydantic
- **Operational data:** PostgreSQL
- **Graph intelligence:** Neo4j and Neo4j Graph Data Science
- **Deployment:** Vercel for the frontend; FastAPI and both databases require separate hosting

Vercel does not host the long-running FastAPI process or PostgreSQL/Neo4j services.

## Prerequisites

- Node.js 20 or later
- Python 3.11 or later
- Docker Desktop
- A running PostgreSQL and Neo4j instance, normally provided by Docker Compose

## Local development

From the repository root, start the databases:

```powershell
docker compose up -d postgres neo4j
```

Start the API in a second terminal:

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Start the frontend in a third terminal:

```powershell
cd frontend
npm ci
Copy-Item .env.example .env.local
npm run dev
```

Open [http://localhost:3000/login](http://localhost:3000/login).

The local API URL must use the same host name as the browser so the development session cookie is sent correctly:

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

The local mock login supports Investigator, Analyst, Supervisor, and Administrator roles. It is enabled only when `APP_ENV=development`, uses an in-memory HttpOnly cookie session, and must not be used for operational or production access.

## Prototype workflow

1. Sign in at `/login` with a prototype role.
2. Review the dashboard service status.
3. Search for `Rohan` and open `Rohan Patil` (`P001`).
4. Inspect the profile, timeline, and bounded network graph.
5. Use graph focus, filters, node/edge details, and depth expansion.
6. Review analytical findings, explanations, evidence, and provenance.
7. Open **Cases** for the CCTNS-inspired FIR/case workspace.

## Quality checks

From the repository root:

```powershell
.\backend\.venv\Scripts\python.exe -m pytest .\tests -q
```

From `frontend/`:

```powershell
npm run lint
npm run build
```

Before a release, verify `/health`, `/health/database`, `/health/neo4j`, entity search, profile, network, timeline, findings, case access, and login/logout behavior.

## Deploy the frontend to Vercel

### 1. Deploy the API and databases first

Deploy FastAPI on a service that supports a persistent process, such as Azure Container Apps, Azure App Service, Render, or Railway. Deploy PostgreSQL and Neo4j using managed services or secured private instances.

The API must be reachable over HTTPS before deploying the frontend.

Configure the API environment with values supplied by your hosting provider:

```text
APP_ENV=production
CORS_ORIGINS=https://your-project.vercel.app
POSTGRES_HOST=your-postgres-host
POSTGRES_PORT=5432
POSTGRES_DB=your-database
POSTGRES_USER=your-database-user
POSTGRES_PASSWORD=your-secret
NEO4J_URI=neo4j+s://your-neo4j-host
NEO4J_USER=your-neo4j-user
NEO4J_PASSWORD=your-secret
```

Use exact HTTPS origins in `CORS_ORIGINS`. Do not use `*` with credentialed requests. Never commit passwords or put them in `NEXT_PUBLIC_*` variables.

### 2. Create the Vercel project

1. Push the repository to GitHub.
2. In Vercel, select **Add New Project** and import the repository.
3. Set **Root Directory** to `frontend`.
4. Select the **Next.js** framework preset.
5. Set **Install Command** to `npm ci`.
6. Set **Build Command** to `npm run build`.
7. Leave **Output Directory** at the Vercel default.

### 3. Configure Vercel environment variables

Add this variable for Preview and Production environments:

```text
NEXT_PUBLIC_API_BASE_URL=https://api.your-domain.example.com
```

Use the public HTTPS URL of the deployed FastAPI service. Redeploy after changing environment variables.

### 4. Configure CORS and verify

Add the final Vercel domain to the API `CORS_ORIGINS`, restart the API, then verify:

- `https://api.your-domain.example.com/health` returns `200`.
- The Vercel app loads without browser CORS errors.
- API requests reach the configured HTTPS backend.
- The synthetic demo label remains visible.

## Authentication limitation

The current login is a development mock only. It is not production authentication: sessions are in memory, there is no durable identity store, MFA, password verification, Entra/OIDC token validation, or production session management. Before exposing NEXUS to real users, replace mock authentication with Microsoft Entra ID/OIDC and enforce validated roles in FastAPI. In `APP_ENV=production`, the mock identity and prototype role headers fail closed.

See [docs/deployment.md](../docs/deployment.md) for the backend deployment checklist.
