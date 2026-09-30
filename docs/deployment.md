# NEXUS deployment preparation

NEXUS is a prototype with a Next.js frontend and a FastAPI backend that uses PostgreSQL for operational case metadata and Neo4j for graph intelligence. Vercel can host the frontend only. Deploy FastAPI, PostgreSQL, and Neo4j separately on services that support long-running processes and persistent databases, then allow the deployed frontend origin in the backend CORS configuration.

## Vercel frontend

Create a Vercel project rooted at `frontend/` with these settings:

- Framework preset: `Next.js`
- Install command: `npm ci`
- Build command: `npm run build`
- Output directory: leave the Vercel default

Set this Vercel environment variable for each environment:

```text
NEXT_PUBLIC_API_BASE_URL=https://api.example.invalid
```

Replace the example value with the HTTPS URL of the separately deployed FastAPI service. Do not put database URLs, Neo4j credentials, client secrets, or access tokens in `NEXT_PUBLIC_*` variables; they are exposed to browser code.

## FastAPI backend

Configure the backend environment with the existing database variables and an explicit frontend allowlist:

```text
APP_ENV=production
CORS_ORIGINS=https://nexus.example.invalid
POSTGRES_HOST=<managed-postgresql-host>
POSTGRES_PORT=5432
POSTGRES_DB=<database-name>
POSTGRES_USER=<database-user>
POSTGRES_PASSWORD=<injected-secret>
NEO4J_URI=neo4j+s://<managed-neo4j-host>
NEO4J_USER=<neo4j-user>
NEO4J_PASSWORD=<injected-secret>
```

`CORS_ORIGINS` is a comma-separated exact-origin list. Include the Vercel production domain and any deliberately supported preview domain; do not use `*` with credentials. The frontend `NEXT_PUBLIC_API_BASE_URL` must point to this backend, and the backend must be reachable over HTTPS.

The development UI uses `POST /auth/mock/login` to issue an in-memory, HttpOnly mock-session cookie. Mock sessions and the backward-compatible `X-Prototype-Role` / `X-Prototype-User-Id` headers work only when `APP_ENV=development`; protected API requests fail closed in every other environment. This is not production authentication: it has no durable identity store, password verification, MFA, Entra/OIDC validation, or production-grade session management.

## Remaining production requirement

Before production access, implement and configure real Entra ID/OIDC authentication and backend authorization. Required values include an approved tenant/issuer, client ID, audience, and secret or certificate where applicable; these must come from the deployment's identity configuration and must not be invented or committed here. Validate tokens server-side and derive roles from trusted claims or an approved authorization store. Frontend-only role checks and request headers are insufficient.

## Local and prototype startup order

From the repository root:

```powershell
docker compose up -d postgres neo4j
backend\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

In a second terminal, from `frontend/`:

```powershell
npm ci
Copy-Item .env.example .env.local
npm run dev
```

Open `http://localhost:3000/login`. The local `.env` keeps `APP_ENV=development`, which is the only mode where synthetic mock sessions and the isolated prototype header fallback are enabled. Configure real Entra ID/OIDC authentication before any non-development deployment. Use `npm run lint` and `npm run build` before deploying the frontend.
