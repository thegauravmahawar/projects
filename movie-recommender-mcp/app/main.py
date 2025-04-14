from typing import List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

from app.config import settings
from app.routers import mcp, admin

from app.tools.search_tools import search_movies, get_movie_by_id, get_top_movies
from app.tools.recommend_tools import recommend_similar_movies, recommend_by_genres, recommend_by_query, recommend_personalized

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

# Include routers
app.include_router(mcp.router, prefix=f"{settings.API_PREFIX}/mcp", tags=["MCP"])
app.include_router(admin.router, prefix=f"{settings.API_PREFIX}/admin", tags=["Admin"])

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

from fastapi import APIRouter
tools_router = APIRouter()

@tools_router.post("/search_movies")
async def search_movies_endpoint(
    query: Optional[str] = None,
    movie_id: Optional[int] = None,
    genres: Optional[List[str]] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    min_rating: Optional[float] = None,
    limit: int = 10
):
    return search_movies(query, movie_id, genres, year_from, year_to, min_rating, limit)

@tools_router.post("/get_movie_by_id")
async def get_movie_endpoint(movie_id: int):
    return get_movie_by_id(movie_id)

@tools_router.get("/get_top_movies")
async def top_movies_endpoint(limit: int = 10):
    return get_top_movies(limit)

@tools_router.post("/recommend_similar_movies")
async def similar_movies_endpoint(movie_id: int, limit: int = 5):
    return recommend_similar_movies(movie_id, limit)

@tools_router.post("/recommend_by_genres")
async def genre_recommendations_endpoint(genres: List[str], limit: int = 5):
    return recommend_by_genres(genres, limit)

@tools_router.post("/recommend_by_query")
async def query_recommendations_endpoint(query: str, limit: int = 5):
    return recommend_by_query(query, limit)

@tools_router.post("/recommend_personalized")
async def personalized_recommendations_endpoint(
    favorite_movies: Optional[List[int]] = None,
    favorite_genres: Optional[List[str]] = None,
    limit: int = 5
):
    return recommend_personalized(favorite_movies, favorite_genres, limit)

# Add this line after the other include_router lines:
app.include_router(tools_router, prefix=f"{settings.API_PREFIX}/tools", tags=["Tools"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)