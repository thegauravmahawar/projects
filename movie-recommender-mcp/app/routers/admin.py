from fastapi import APIRouter, HTTPException, BackgroundTasks
import logging
from typing import Dict, List, Any

from app.services.chromadb_service import populate_chroma_from_data
from app.data.loader import download_and_extract_dataset, get_popular_movies

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/populate-database")
async def populate_database(background_tasks: BackgroundTasks):
    """
    Populate the ChromaDB database with movie data

    Args:
        background_tasks: FastAPI background tasks

    Returns:
        Confirmation message
    """
    logger.info("Starting database population")

    try:
        # Download dataset if needed
        download_and_extract_dataset()

        # Add to background tasks to avoid blocking the response
        background_tasks.add_task(populate_chroma_from_data)

        return {"message": "Database population started in the background"}
    except Exception as e:
        logger.error(f"Error starting database population: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/popular-movies")
async def get_popular_movies_endpoint(limit: int = 10):
    """
    Get the most popular movies

    Args:
        limit: Maximum number of movies to return

    Returns:
        List of popular movies
    """
    try:
        movies = get_popular_movies(limit=limit)
        return {"movies": movies}
    except Exception as e:
        logger.error(f"Error getting popular movies: {e}")
        raise HTTPException(status_code=500, detail=str(e))