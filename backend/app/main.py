import logging
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from neo4j.exceptions import Neo4jError
from .api.entities import router as entities_router
from .api.findings import router as findings_router
from .api.cases import router as cases_router
from .config import settings

from sqlalchemy import text

from .database import engine
from .graph import check_neo4j, close_driver, driver


app = FastAPI(
    title="NEXUS API",
    version="0.1.0",
    description="Explainable Criminal Network Intelligence System",
)

logger = logging.getLogger(__name__)


@app.exception_handler(Neo4jError)
async def neo4j_error_handler(
    request: Request,
    exc: Neo4jError,
) -> JSONResponse:
    """Keep graph-driver details in logs, not API responses."""
    request_id = uuid4().hex
    logger.exception("Neo4j request failed for %s", request.url.path)
    return JSONResponse(
        status_code=503,
        headers={"X-Request-ID": request_id},
        content={
            "error": "GRAPH_DATABASE_UNAVAILABLE",
            "message": "Network intelligence service is temporarily unavailable. Please retry.",
            "request_id": request_id,
            "details": None,
        },
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    findings_router
)

app.include_router(
    entities_router
)
app.include_router(cases_router)


@app.on_event("shutdown")
def shutdown_graph_driver() -> None:
    close_driver()

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
        logger.exception("PostgreSQL health check failed")
        raise HTTPException(
            status_code=503,
            detail="PostgreSQL is unavailable.",
        ) from exc


@app.get("/health/neo4j")
def neo4j_health():
    try:
        working = check_neo4j()

        return {
            "status": "ok" if working else "error",
            "database": "neo4j",
        }

    except Exception as exc:
        logger.exception("Neo4j health check failed")
        raise HTTPException(
            status_code=503,
            detail="Neo4j is unavailable.",
        ) from exc
