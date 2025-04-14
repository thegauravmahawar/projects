from fastapi import APIRouter, HTTPException, Depends, Body, BackgroundTasks
import logging
import json
from typing import Dict, List, Any, Optional
import uuid

from app.models.mcp_models import MCPRequest, MCPResponse, Message, MessageRole, FunctionCall, FunctionDefinition
from app.services.llm_service import call_llm
from app.utils.prompt_templates import get_system_prompt
from app.tools.search_tools import search_movies, get_movie_by_id, get_top_movies
from app.tools.recommend_tools import recommend_similar_movies, recommend_by_genres, recommend_by_query, recommend_personalized

logger = logging.getLogger(__name__)

router = APIRouter()

# Function registry
# Maps function names to their implementations and definitions
function_registry = {
    "search_movies": {
        "func": search_movies,
        "definition": FunctionDefinition(
            name="search_movies",
            description="Search for movies based on various criteria",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Text query to search for"
                    },
                    "movie_id": {
                        "type": "integer",
                        "description": "Find movies similar to this one"
                    },
                    "genres": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "List of genres to filter by"
                    },
                    "year_from": {
                        "type": "integer",
                        "description": "Minimum release year"
                    },
                    "year_to": {
                        "type": "integer",
                        "description": "Maximum release year"
                    },
                    "min_rating": {
                        "type": "number",
                        "description": "Minimum average rating"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 10
                    }
                },
                "required": []
            }
        )
    },
    "get_movie_by_id": {
        "func": get_movie_by_id,
        "definition": FunctionDefinition(
            name="get_movie_by_id",
            description="Get details for a specific movie",
            parameters={
                "type": "object",
                "properties": {
                    "movie_id": {
                        "type": "integer",
                        "description": "MovieLens movie ID"
                    }
                },
                "required": ["movie_id"]
            }
        )
    },
    "get_top_movies": {
        "func": get_top_movies,
        "definition": FunctionDefinition(
            name="get_top_movies",
            description="Get the top rated/popular movies",
            parameters={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of movies to return",
                        "default": 10
                    }
                },
                "required": []
            }
        )
    },
    "recommend_similar_movies": {
        "func": recommend_similar_movies,
        "definition": FunctionDefinition(
            name="recommend_similar_movies",
            description="Recommend movies similar to the given movie",
            parameters={
                "type": "object",
                "properties": {
                    "movie_id": {
                        "type": "integer",
                        "description": "ID of the movie to find similar movies for"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of recommendations",
                        "default": 5
                    }
                },
                "required": ["movie_id"]
            }
        )
    },
    "recommend_by_genres": {
        "func": recommend_by_genres,
        "definition": FunctionDefinition(
            name="recommend_by_genres",
            description="Recommend movies based on specified genres",
            parameters={
                "type": "object",
                "properties": {
                    "genres": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "List of genres to base recommendations on"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of recommendations",
                        "default": 5
                    }
                },
                "required": ["genres"]
            }
        )
    },
    "recommend_by_query": {
        "func": recommend_by_query,
        "definition": FunctionDefinition(
            name="recommend_by_query",
            description="Recommend movies based on a text query",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Text query describing what the user is looking for"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of recommendations",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        )
    },
    "recommend_personalized": {
        "func": recommend_personalized,
        "definition": FunctionDefinition(
            name="recommend_personalized",
            description="Generate personalized recommendations based on user preferences",
            parameters={
                "type": "object",
                "properties": {
                    "favorite_movies": {
                        "type": "array",
                        "items": {
                            "type": "integer"
                        },
                        "description": "List of IDs of user's favorite movies"
                    },
                    "favorite_genres": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "List of user's favorite genres"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of recommendations",
                        "default": 5
                    }
                },
                "required": []
            }
        )
    }
}

async def execute_function_call(function_call: FunctionCall) -> Dict[str, Any]:
    """
    Execute a function call based on the function registry

    Args:
        function_call: FunctionCall object with name and arguments

    Returns:
        The result of the function call
    """
    function_name = function_call.name

    if function_name not in function_registry:
        raise ValueError(f"Unknown function: {function_name}")

    function = function_registry[function_name]["func"]
    arguments = function_call.arguments

    try:
        logger.info(f"Executing function {function_name} with arguments {arguments}")
        result = function(**arguments)
        return result
    except Exception as e:
        logger.error(f"Error executing function {function_name}: {e}")
        raise

@router.post("/chat", response_model=MCPResponse)
async def chat(request: MCPRequest, background_tasks: BackgroundTasks):
    """Process a chat request through the MCP server"""
    # Create a new session ID if one isn't provided
    if not request.context.session_id:
        request.context.session_id = str(uuid.uuid4())

    # Add system message if not present
    system_message_present = any(
        message.role == MessageRole.SYSTEM for message in request.messages
    )

    if not system_message_present:
        system_prompt = get_system_prompt(request.context.favorite_genres)
        request.messages.insert(0, Message(
            role=MessageRole.SYSTEM,
            content=system_prompt
        ))

    # Get function definitions
    function_definitions = [
        registry_item["definition"] for registry_item in function_registry.values()
    ]

    # Call the LLM
    try:
        response = await call_llm(
            messages=request.messages,
            functions=function_definitions,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=False
        )

        # Extract the assistant message - ensure content is never None
        content = response["choices"][0]["message"].get("content")
        if content is None:
            content = ""

        assistant_message = Message(
            role=MessageRole.ASSISTANT,
            content=content
        )

        # Extract function call if present
        function_call = None
        if "function_call" in response["choices"][0]["message"]:
            fc = response["choices"][0]["message"]["function_call"]
            try:
                function_call = FunctionCall(
                    name=fc["name"],
                    arguments=json.loads(fc["arguments"])
                )
            except json.JSONDecodeError:
                logger.error(f"Failed to parse function arguments: {fc['arguments']}")
                function_call = FunctionCall(
                    name=fc["name"],
                    arguments={}
                )

            # Execute the function call
            try:
                result = await execute_function_call(function_call)

                # Add function result as a new message
                result_json = json.dumps(result) if result is not None else "{}"
                function_response = Message(
                    role=MessageRole.FUNCTION,
                    content=result_json,
                    name=function_call.name
                )

                # Call the LLM again with the function result
                new_messages = request.messages + [
                    Message(
                        role=MessageRole.ASSISTANT,
                        content="",
                        name=None
                    ),
                    function_response
                ]

                # Add explicit instructions to the system message
                processing_instructions = """
                You'll now receive results from a function call.
                Please format these results into a natural, conversational response.
                If the result contains movie information, describe the movies in a helpful way.
                Always provide a complete response based on the function results.
                """

                explicit_msg = Message(
                    role=MessageRole.SYSTEM,
                    content=processing_instructions
                )

                new_messages.append(explicit_msg)

                final_response = await call_llm(
                    messages=new_messages,
                    functions=function_definitions,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    stream=False
                )

                # Update assistant message with the final response
                final_content = final_response["choices"][0]["message"].get("content")
                if final_content is None or final_content.strip() == "":
                    # Fallback if the LLM still doesn't generate a good response
                    if function_call.name == "search_movies":
                        movies = result
                        if movies and len(movies) > 0:
                            final_content = "I found the following movies that match your query:\n\n"
                            for i, movie in enumerate(movies[:5], 1):
                                title = movie.get("title", "Unknown")
                                year = f" ({movie.get('year')})" if movie.get("year") else ""
                                genres = ", ".join(movie.get("genres", [])) if movie.get("genres") else "Unknown Genre"
                                final_content += f"{i}. {title}{year} - {genres}\n"
                        else:
                            final_content = "I searched for movies matching your query, but couldn't find any results."
                    elif function_call.name == "get_movie_by_id":
                        movie = result
                        if movie:
                            title = movie.get("title", "Unknown")
                            year = f" ({movie.get('year')})" if movie.get("year") else ""
                            genres = ", ".join(movie.get("genres", [])) if movie.get("genres") else "Unknown Genre"
                            final_content = f"Here are details about {title}{year}:\nGenres: {genres}\n"
                        else:
                            final_content = "I tried to find that movie, but couldn't retrieve any details."
                    else:
                        # Generic fallback for other functions
                        final_content = f"I found some information for you based on your request. Here's what I found:\n\n{json.dumps(result, indent=2)}"

                assistant_message = Message(
                    role=MessageRole.ASSISTANT,
                    content=final_content
                )
            except Exception as e:
                logger.error(f"Error executing function call: {e}")
                # Return error to the client
                assistant_message = Message(
                    role=MessageRole.ASSISTANT,
                    content=f"I encountered an error while trying to process your request: {str(e)}"
                )

        # Create the MCP response
        mcp_response = MCPResponse(
            message=assistant_message,
            function_call=function_call,
            context_update={}
        )

        return mcp_response

    except Exception as e:
        logger.error(f"Error processing MCP request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}