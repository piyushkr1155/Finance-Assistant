from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from api.upload import router as upload_router
from api.analytics import router as analytics_router
from api.ai import router as ai_router
from services.ai_provider import ai_service

app = FastAPI(
    title="LocalLedger AI API",
    description="Privacy-first, local-AI-powered financial assistant for small businesses.",
    version="1.0.0",
)

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import JSONResponse
from fastapi import Request
import traceback

# Register API Routers
app.include_router(upload_router)
app.include_router(analytics_router)
app.include_router(ai_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all exception handler ensuring zero unformatted stack traces
    leak to end users. Full diagnostic traceback is recorded to server stderr.
    """
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred while processing your request. Please try again or check server logs.",
        },
    )


@app.get("/")
def read_root():
    return {
        "project": "LocalLedger AI",
        "status": "online",
        "version": "1.0.0",
        "docs_url": "/docs",
    }


@app.get("/api/health")
def health_check():
    ai_status = ai_service.get_status()
    return {
        "status": "ok",
        "service": "localledger-backend",
        "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
        "ollama_available": ai_status.available,
        "active_model": ai_status.active_model,
        "available_models": ai_status.available_models,
        "message": ai_status.message,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
