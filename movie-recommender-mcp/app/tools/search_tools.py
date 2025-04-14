from typing import List, Dict, Any, Optional
import logging
import re

from app.services.chromadb_service import search_similar_movies
from app.data.loader import get_movie_details, get_popular_movies, load_movie_data

logger = logging.getLogger(__name__)

def normalize_text(text: str) -> str:
    """Normalize text for better matching"""
    if not text:
        return ""
    # Convert to lowercase, remove extra spaces, and strip punctuation
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)
    return text

def search_movies(
    query: Optional[str] = None,
    movie_id: Optional[int] = None,
    genres: Optional[List[str]] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    min_rating: Optional[float] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Search for movies based on various criteria

    Args:
        query: Text query to search for
        movie_id: Find movies similar to this one
        genres: List of genres to filter by
        year_from: Minimum release year
        year_to: Maximum release year
        min_rating: Minimum average rating
        limit: Maximum number of results

    Returns:
        List of matching movies
    """
    logger.info(f"Searching for movies: query={query}, movie_id={movie_id}, genres={genres}")

    # Try ChromaDB search first
    try:
        # Prepare filter dictionary for ChromaDB
        filter_dict = {}

        # Year filtering
        if year_from:
            filter_dict["year"] = {"$gte": str(year_from)}

        if year_to:
            if "year" in filter_dict:
                filter_dict["year"]["$lte"] = str(year_to)
            else:
                filter_dict["year"] = {"$lte": str(year_to)}

        results = []

        # If we have a query or movie_id, use semantic search
        if query or movie_id:
            # Try ChromaDB search
            try:
                results = search_similar_movies(
                    query_text=query,
                    movie_id=movie_id,
                    filter_dict=filter_dict,
                    limit=limit * 3  # Get more to filter later
                )
            except Exception as e:
                logger.warning(f"ChromaDB search failed, falling back to direct search: {e}")
                results = []

        # If no results from semantic search or no query specified, try direct matching
        if not results:
            logger.info("No semantic search results, trying direct title matching")

            # Load all movies
            movies_df = load_movie_data()

            if query:
                # Normalize the query
                normalized_query = normalize_text(query)

                # First try exact title match
                matches = []
                for _, row in movies_df.iterrows():
                    title = normalize_text(row["title_clean"])

                    # Check for exact match
                    if normalized_query == title:
                        matches.append({
                            "id": int(row["movieId"]),
                            "title": row["title_clean"],
                            "year": row["year"],
                            "genres": row["genres"],
                            "match_type": "exact"
                        })
                    # Check for title containing query
                    elif normalized_query in title:
                        matches.append({
                            "id": int(row["movieId"]),
                            "title": row["title_clean"],
                            "year": row["year"],
                            "genres": row["genres"],
                            "match_type": "partial"
                        })

                # Sort exact matches first, then partial matches
                matches.sort(key=lambda x: 0 if x.get("match_type") == "exact" else 1)
                results = matches[:limit * 3]  # Get more to filter later

                logger.info(f"Direct title matching found {len(results)} results")
            else:
                # If no query and no semantic results, use popular movies
                results = get_popular_movies(limit=limit)

        # Apply genre filtering if needed
        if genres and len(genres) > 0:
            filtered_results = []
            normalized_genres = [normalize_text(g) for g in genres]

            for movie in results:
                movie_genres = [normalize_text(g) for g in movie.get("genres", [])]
                # Check if any of the specified genres match
                if any(genre in movie_genres for genre in normalized_genres):
                    filtered_results.append(movie)

            results = filtered_results
            logger.info(f"After genre filtering: {len(results)} results")

        # Apply limit
        results = results[:limit]

        # Convert to consistent format
        movies = []
        for result in results:
            movie = {
                "id": result["id"],
                "title": result["title"],
                "year": result.get("year"),
                "genres": result.get("genres", []),
            }

            # Add additional fields if available
            if "avg_rating" in result:
                movie["avg_rating"] = result["avg_rating"]
            if "num_ratings" in result:
                movie["num_ratings"] = result["num_ratings"]
            if "similarity" in result:
                movie["similarity"] = result["similarity"]

            movies.append(movie)

        logger.info(f"Found {len(movies)} movies matching criteria")
        return movies

    except Exception as e:
        logger.error(f"Error in search_movies: {e}")
        return []

def get_movie_by_id(movie_id: int) -> Dict[str, Any]:
    """
    Get details for a specific movie

    Args:
        movie_id: MovieLens movie ID

    Returns:
        Movie details dictionary
    """
    logger.info(f"Getting details for movie {movie_id}")
    try:
        movie = get_movie_details(movie_id)
        logger.info(f"Found movie: {movie.get('title', 'Unknown')}")
        return movie
    except Exception as e:
        logger.error(f"Error getting movie details for ID {movie_id}: {e}")
        return {"error": f"Movie with ID {movie_id} not found", "id": movie_id}

def get_top_movies(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get the top rated/popular movies

    Args:
        limit: Maximum number of movies to return

    Returns:
        List of top movies
    """
    logger.info(f"Getting top {limit} movies")
    return get_popular_movies(limit=limit)