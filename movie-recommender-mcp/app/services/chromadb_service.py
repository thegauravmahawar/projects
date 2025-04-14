import logging
import os
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional, Union

from app.config import settings
from app.services.embeddings import generate_embedding, generate_movie_embedding

logger = logging.getLogger(__name__)

# Singleton for the ChromaDB client
_client = None

def get_chroma_client():
    """Get or initialize the ChromaDB client"""
    global _client

    if _client is None:
        # Make sure the persist directory exists
        os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)

        try:
            logger.info(f"Initializing ChromaDB client with persistence at {settings.CHROMA_PERSIST_DIRECTORY}")
            _client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIRECTORY,
                settings=ChromaSettings(
                    anonymized_telemetry=False
                )
            )

            # Initialize default collections
            _ensure_collections_exist(_client)

        except Exception as e:
            logger.error(f"Error initializing ChromaDB client: {e}")
            raise

    return _client

def _ensure_collections_exist(client):
    """Ensure that the required collections exist"""
    # Movies collection
    try:
        client.get_collection("movies")
        logger.info("Movies collection already exists")
    except:
        # Create the collection
        client.create_collection(
            name="movies",
            metadata={"description": "Movie embeddings for recommendation"}
        )
        logger.info("Movies collection created")

def add_movie_to_chroma(movie: Dict[str, Any]) -> str:
    """
    Add a movie to the ChromaDB collection

    Args:
        movie: Movie data dictionary

    Returns:
        ID of the document in ChromaDB
    """
    client = get_chroma_client()
    collection = client.get_collection("movies")

    # Generate embedding
    embedding = generate_movie_embedding(movie)

    # Document ID
    doc_id = f"movie_{movie['id']}"

    # Construct metadata (must be strings for ChromaDB)
    metadata = {
        "movie_id": str(movie["id"]),
        "title": movie["title"],
        "year": str(movie["year"]) if movie.get("year") else "",
        "genres": ",".join(movie["genres"]) if movie.get("genres") else "",
    }

    # Create document text
    document = f"Title: {movie['title']}\n"
    if movie.get("year"):
        document += f"Year: {movie['year']}\n"
    if movie.get("genres"):
        document += f"Genres: {', '.join(movie['genres'])}\n"

    # Add to collection
    try:
        # Check if it already exists
        try:
            collection.get(ids=[doc_id])
            # Update if it exists
            collection.update(
                ids=[doc_id],
                embeddings=[embedding],
                metadatas=[metadata],
                documents=[document]
            )
            logger.debug(f"Updated movie {movie['id']} in ChromaDB")
        except:
            # Add if it doesn't exist
            collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                metadatas=[metadata],
                documents=[document]
            )
            logger.debug(f"Added movie {movie['id']} to ChromaDB")

        return doc_id
    except Exception as e:
        logger.error(f"Error adding movie {movie['id']} to ChromaDB: {e}")
        raise

def search_similar_movies(
    query_text: Optional[str] = None,
    movie_id: Optional[int] = None,
    filter_dict: Optional[Dict[str, str]] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Search for similar movies in ChromaDB

    Args:
        query_text: Text to search for (will be converted to embedding)
        movie_id: Movie ID to find similar movies for
        filter_dict: Dictionary of metadata filters
        limit: Maximum number of results to return

    Returns:
        List of similar movies with metadata
    """
    client = get_chroma_client()
    collection = client.get_collection("movies")

    # Determine query method
    if movie_id is not None:
        # Get embedding for the specified movie
        doc_id = f"movie_{movie_id}"
        try:
            result = collection.get(ids=[doc_id], include=["embeddings"])
            if not result["embeddings"]:
                raise ValueError(f"Movie with ID {movie_id} not found in database")
            query_embedding = result["embeddings"][0]
        except Exception as e:
            logger.error(f"Error retrieving movie {movie_id}: {e}")
            raise
    elif query_text is not None:
        # Generate embedding from text
        query_embedding = generate_embedding(query_text)
    else:
        raise ValueError("Either query_text or movie_id must be provided")

    # Prepare where clause for filtering
    where = {}
    if filter_dict:
        where = filter_dict

    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            where=where if where else None
        )

        # Process and return results
        movies = []
        for i, (id, metadata, document) in enumerate(zip(
                results["ids"][0],
                results["metadatas"][0],
                results["documents"][0]
            )):

            # Extract similarity score if available
            similarity = 1.0 - results["distances"][0][i] if "distances" in results else None

            # Parse genres from string
            genres = metadata["genres"].split(",") if metadata.get("genres") else []

            movie = {
                "id": int(metadata["movie_id"]),
                "title": metadata["title"],
                "year": metadata["year"] if metadata.get("year") else None,
                "genres": genres,
                "similarity": similarity,
                "document": document
            }
            movies.append(movie)

        return movies

    except Exception as e:
        logger.error(f"Error searching ChromaDB: {e}")
        raise

def populate_chroma_from_data():
    """Populate ChromaDB with movie data from the MovieLens dataset"""
    from app.data.loader import load_movie_data

    # Load movie data
    movies_df = load_movie_data()

    # Add each movie to ChromaDB
    total = len(movies_df)
    logger.info(f"Adding {total} movies to ChromaDB")

    for idx, row in movies_df.iterrows():
        movie = {
            "id": int(row["movieId"]),
            "title": row["title_clean"],
            "year": row["year"],
            "genres": row["genres"]
        }

        add_movie_to_chroma(movie)

        # Log progress
        if (idx + 1) % 100 == 0:
            logger.info(f"Progress: {idx + 1}/{total} movies added to ChromaDB")

    logger.info("Finished adding movies to ChromaDB")