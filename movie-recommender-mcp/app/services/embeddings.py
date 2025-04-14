import logging
from typing import List, Dict, Any, Optional, Union
import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import settings

logger = logging.getLogger(__name__)

# Singleton for the embedding model
_model = None

def get_embedding_model():
    """Get or initialize the embedding model"""
    global _model

    if _model is None:
        try:
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME}")
            _model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise

    return _model

def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for a text string

    Args:
        text: Text to generate embedding for

    Returns:
        List of floats representing the embedding vector
    """
    model = get_embedding_model()

    try:
        embedding = model.encode(text)
        return embedding.tolist()
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise

def generate_movie_embedding(movie: Dict[str, Any]) -> List[float]:
    """
    Generate embedding for a movie

    Args:
        movie: Movie data dictionary

    Returns:
        Embedding vector for the movie
    """
    # Create a text representation of the movie
    text_parts = []

    if "title" in movie:
        text_parts.append(f"Title: {movie['title']}")

    if "genres" in movie and movie["genres"]:
        genres_text = ", ".join(movie["genres"])
        text_parts.append(f"Genres: {genres_text}")

    if "year" in movie and movie["year"]:
        text_parts.append(f"Year: {movie['year']}")

    # Combine all parts
    movie_text = " ".join(text_parts)

    # Generate embedding
    return generate_embedding(movie_text)