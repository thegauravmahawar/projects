from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Set

class Movie(BaseModel):
    """Movie model"""
    id: int
    title: str
    year: Optional[str] = None
    genres: List[str] = []
    avg_rating: Optional[float] = None
    num_ratings: Optional[int] = None
    similarity: Optional[float] = None

class MovieSearchParams(BaseModel):
    """Movie search parameters"""
    query: Optional[str] = None
    movie_id: Optional[int] = None
    genres: Optional[List[str]] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    min_rating: Optional[float] = None
    limit: int = 10

class MovieRecommendation(BaseModel):
    """Movie recommendation model"""
    movie: Movie
    reason: Optional[str] = None

class RecommendationRequest(BaseModel):
    """Recommendation request model"""
    user_id: Optional[str] = None
    movie_id: Optional[int] = None
    genres: Optional[List[str]] = None
    query: Optional[str] = None
    limit: int = 5