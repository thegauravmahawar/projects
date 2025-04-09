from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

from app.config import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url=f"{settings.API_PREFIX}/docs",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
# Will add these later as we implement them

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Movie Recommendation MCP Server")

    # Create necessary directories
    os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    os.makedirs(settings.PROCESSED_DATA_DIR, exist_ok=True)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Movie Recommendation MCP Server",
        "docs": f"{settings.API_PREFIX}/docs",
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)