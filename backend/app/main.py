from fastapi import FastAPI

app = FastAPI(
    title="NEXUS API",
    version="0.1.0",
    description="Explainable Criminal Network Intelligence System",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "NEXUS API",
        "version": "0.1.0",
    }