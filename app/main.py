from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.api.v1.reports import router as reports_router

from app.db.session import engine

app = FastAPI(
    title="Ridevo API",
    description="AI-powered used car listing analysis API.",
    version="0.1.0",
)

app.include_router(reports_router, prefix="/api/v1")

@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "ridevo-api",
    }

@app.get("/ready", tags=["Health"])
def readiness_check() -> dict[str, str]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed",
        ) from exc

    return {
        "status": "ready",
        "database": "connected",
    }