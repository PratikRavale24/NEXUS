from fastapi import FastAPI
from .api.findings import router as findings_router

from sqlalchemy import text

from .database import engine


app = FastAPI(
    title="NEXUS API",
    version="0.1.0",
    description="Explainable Criminal Network Intelligence System",
)

app.include_router(
    findings_router
)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "NEXUS API",
        "version": "0.1.0",
    }


@app.get("/health/database")
def database_health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "database": "postgresql",
        }

    except Exception as exc:
        return {
            "status": "error",
            "database": "postgresql",
            "detail": str(exc),
        }


from .graph import check_neo4j


@app.get("/health/neo4j")
def neo4j_health():
    try:
        working = check_neo4j()

        return {
            "status": "ok" if working else "error",
            "database": "neo4j",
        }

    except Exception as exc:
        return {
            "status": "error",
            "database": "neo4j",
            "detail": str(exc),
        }