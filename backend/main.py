from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from api.upload import router as upload_router

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

# Register API Routers
app.include_router(upload_router)


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
    return {
        "status": "ok",
        "service": "localledger-backend",
        "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
