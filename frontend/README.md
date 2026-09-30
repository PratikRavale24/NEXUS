# NEXUS frontend

NEXUS is an explainable criminal-network intelligence prototype for authorized investigative analysis. It uses a deterministic synthetic dataset; analytical indicators are investigative leads, not guilt determinations.

## Start locally

From the repository root, start PostgreSQL and Neo4j with Docker Compose, then start the FastAPI service:

```powershell
.\backend\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

In this directory, create `frontend/.env.local` with the public API URL if the default is not suitable:

```text
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

Then run:

```powershell
npm.cmd run dev
```

Open `http://localhost:3000`.

## Demo flow

1. Open the dashboard and select **Open Rohan Patil**.
2. Inspect the entity record, relationship graph, and chronology.
3. Open **Findings** and choose an anomaly or temporal-coordination candidate.
4. Review the explanation and source-linked evidence.
5. Add investigator notes and mark the candidate under review.

## Checks

```powershell
npm.cmd run lint
npm.cmd run build
```

The frontend expects the API routes for health, entities, network, timeline, findings, evidence references, and finding review. Neo4j remains the active graph integration; no demo fallback is used while it is available.
