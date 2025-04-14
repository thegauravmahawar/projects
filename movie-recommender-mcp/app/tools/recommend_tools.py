from typing import List, Dict, Any, Optional
import logging
import random
from collections import Counter

from app.tools.search_tools import search_movies, get_movie_by_id
from app.services.chromadb_service import search_similar_movies

logger = logging.getLogger(__name__)

def recommend_similar_movies(movie_id: int, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Recommend movies similar to the given movie

    Args:
        movie_id: ID of the movie to find similar movies for
        limit: Maximum number of recommendations

    Returns:
        List of similar movie recommendations
    """
    logger.info(f"Finding movies similar to movie {movie_id}")

    # Get the source movie
    source_movie = get_movie_by_id(movie_id)

    # Find similar movies using ChromaDB
    similar_movies = search_similar_movies(
        movie_id=movie_id,
        limit=limit + 1  # Add 1 because the movie itself might be included
    )

    # Filter out the source movie
    recommendations = [
        movie for movie in similar_movies
        if movie["id"] != movie_id
    ][:limit]

    # Add recommendation reasons
    for movie in recommendations:
        # Generate a reason based on similarity to the source movie
        genres_overlap = set(movie.get("genres", [])) & set(source_movie.get("genres", []))

        if genres_overlap:
            genre_reason = f"shares genres like {', '.join(list(genres_overlap)[:2])}"
            if movie.get("year") and source_movie.get("year"):
                year_diff = abs(int(movie.get("year") or 0) - int(source_movie.get("year") or 0))
                if year_diff <= 5:
                    movie["reason"] = f"This movie {genre_reason} and was released around the same time."
                else:
                    movie["reason"] = f"This movie {genre_reason}, although from a different era."
            else:
                movie["reason"] = f"This movie {genre_reason} with {source_movie['title']}."
        else:
            movie["reason"] = f"This movie has a similar style and mood to {source_movie['title']}."

    return recommendations

def recommend_by_genres(genres: List[str], limit: int = 5) -> List[Dict[str, Any]]:
    """
    Recommend movies based on specified genres

    Args:
        genres: List of genres to base recommendations on
        limit: Maximum number of recommendations

    Returns:
        List of movie recommendations
    """
    logger.info(f"Finding movies with genres: {genres}")

    # Search for movies with the specified genres
    movies = search_movies(genres=genres, limit=limit)

    # Add recommendation reasons
    for movie in movies:
        matched_genres = set(movie.get("genres", [])) & set(genres)
        genres_text = ", ".join(list(matched_genres)[:2])
        movie["reason"] = f"This movie features {genres_text} that you're interested in."

    return movies

def recommend_by_query(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Recommend movies based on a text query

    Args:
        query: Text query describing what the user is looking for
        limit: Maximum number of recommendations

    Returns:
        List of movie recommendations
    """
    logger.info(f"Finding movies matching query: {query}")

    # Use semantic search to find matching movies
    movies = search_movies(query=query, limit=limit)

    # Add recommendation reasons
    for movie in movies:
        movie["reason"] = f"This movie matches your search for '{query}'."

    return movies

def recommend_personalized(
    favorite_movies: Optional[List[int]] = None,
    favorite_genres: Optional[List[str]] = None,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Generate personalized recommendations based on user preferences

    Args:
        favorite_movies: List of IDs of user's favorite movies
        favorite_genres: List of user's favorite genres
        limit: Maximum number of recommendations

    Returns:
        List of personalized movie recommendations
    """
    logger.info(f"Generating personalized recommendations based on: favorite_movies={favorite_movies}, favorite_genres={favorite_genres}")

    recommendations = []

    # If user has favorite movies, use them for recommendations
    if favorite_movies and len(favorite_movies) > 0:
        # Pick a random favorite movie to find similar movies
        random_favorite = random.choice(favorite_movies)
        similar_recs = recommend_similar_movies(random_favorite, limit=limit // 2)
        recommendations.extend(similar_recs)

    # If user has favorite genres, use them for recommendations
    if favorite_genres and len(favorite_genres) > 0:
        # Use all favorite genres for recommendations
        genre_recs = recommend_by_genres(favorite_genres, limit=limit - len(recommendations))

        # Filter out duplicates
        existing_ids = {movie["id"] for movie in recommendations}
        unique_genre_recs = [movie for movie in genre_recs if movie["id"] not in existing_ids]

        recommendations.extend(unique_genre_recs[:limit - len(recommendations)])

    # If we still need more recommendations, add popular movies
    if len(recommendations) < limit:
        from app.data.loader import get_popular_movies
        popular_movies = get_popular_movies(limit=limit - len(recommendations))

        # Filter out duplicates
        existing_ids = {movie["id"] for movie in recommendations}
        unique_popular = [movie for movie in popular_movies if movie["id"] not in existing_ids]

        for movie in unique_popular:
            movie["reason"] = "This is a popular movie that many users enjoy."

        recommendations.extend(unique_popular)

    return recommendations[:limit]