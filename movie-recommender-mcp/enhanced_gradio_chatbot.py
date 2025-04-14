import gradio as gr
import requests
import uuid
import json
import logging
from typing import List, Dict, Any, Tuple, Optional
import time
import traceback
import os

# Configure logging with file output
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("chatbot_debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# MCP Server connection settings
MCP_SERVER_URL = "http://localhost:8000/api/mcp/chat"
ADMIN_URL = "http://localhost:8000/api/admin"
SESSION_ID = str(uuid.uuid4())  # Generate a session ID for this chat instance

# Chat state
class ChatState:
    def __init__(self):
        self.message_history = []
        self.favorite_genres = []
        self.favorite_movies = []
        self.recent_searches = []
        self.session_id = SESSION_ID

chat_state = ChatState()

def format_movie_list(movies: List[Dict[str, Any]]) -> str:
    """Format a list of movies into a readable string"""
    if not movies:
        return "No movies found."

    result = ""
    for i, movie in enumerate(movies, 1):
        # Basic movie info
        title = movie.get("title", "Unknown Title")
        year = f" ({movie.get('year')})" if movie.get("year") else ""
        genres = ", ".join(movie.get("genres", [])) if movie.get("genres") else "Unknown Genre"

        # Additional details if available
        rating = f", Rating: {movie.get('avg_rating'):.1f}/5" if movie.get("avg_rating") else ""
        similarity = f", Similarity: {movie.get('similarity'):.2f}" if movie.get("similarity") else ""
        reason = f"\n   Reason: {movie.get('reason')}" if movie.get("reason") else ""

        result += f"{i}. {title}{year} - {genres}{rating}{similarity}{reason}\n\n"

    return result

def send_message_to_mcp(message: str, history: List[List[str]]) -> Tuple[str, List[List[str]]]:
    """Send a message to the MCP server and get a response"""
    global chat_state

    # Log the incoming message
    logger.info(f"User message: {message}")

    # Prepare the request payload
    mcp_messages = []

    # Add history to provide context
    for human_msg, ai_msg in history:
        if human_msg is not None:  # Skip initial welcome message
            mcp_messages.append({"role": "user", "content": human_msg})
            mcp_messages.append({"role": "assistant", "content": ai_msg})

    # Add the current message
    mcp_messages.append({"role": "user", "content": message})

    # Prepare the request payload
    payload = {
        "messages": mcp_messages,
        "context": {
            "session_id": chat_state.session_id,
            "favorite_genres": chat_state.favorite_genres,
            "favorite_movies": chat_state.favorite_movies,
            "recent_searches": chat_state.recent_searches
        }
    }

    # Log the complete payload being sent
    logger.debug(f"Sending MCP request payload: {json.dumps(payload, indent=2)}")

    try:
        # Show thinking state
        new_history = history + [[message, "Thinking..."]]
        yield "", new_history

        # Send the request to the MCP server
        logger.info(f"Sending request to MCP server")
        response = requests.post(MCP_SERVER_URL, json=payload)

        # Log the raw response
        logger.debug(f"Raw MCP response: Status {response.status_code}, Content: {response.text[:1000]}...")

        response.raise_for_status()  # Raise an exception for 4XX/5XX responses

        mcp_response = response.json()
        logger.info(f"Received response from MCP server")

        # Extract the assistant's message
        assistant_message = mcp_response.get("message", {}).get("content", "")
        logger.info(f"Assistant message: {assistant_message[:100]}...")

        # Check if there was a function call and log it
        function_call = mcp_response.get("function_call")
        if function_call:
            function_name = function_call.get("name", "")
            arguments = function_call.get("arguments", {})
            logger.info(f"Function called: {function_name} with arguments: {json.dumps(arguments)}")

            # Log the direct function call attempt
            try:
                # Only for get_movie_by_id, we'll make a direct call to debug
                if function_name == "get_movie_by_id":
                    movie_id = arguments.get("movie_id")
                    logger.info(f"Directly calling get_movie_by_id with movie_id={movie_id}")

                    # Make a direct API call to the tools endpoint
                    direct_url = f"http://localhost:8000/api/tools/get_movie_by_id"
                    direct_response = requests.post(direct_url, json={"movie_id": movie_id})

                    logger.info(f"Direct API call response: Status {direct_response.status_code}")
                    logger.debug(f"Direct API call content: {direct_response.text}")
            except Exception as direct_err:
                logger.error(f"Error in direct function call: {direct_err}")

        # Update context if provided
        context_update = mcp_response.get("context_update", {})
        if context_update:
            logger.info(f"Context update received: {context_update}")
            if "favorite_genres" in context_update:
                chat_state.favorite_genres = context_update["favorite_genres"]
            if "favorite_movies" in context_update:
                chat_state.favorite_movies = context_update["favorite_movies"]
            if "recent_searches" in context_update:
                chat_state.recent_searches = context_update["recent_searches"]

        # Update history
        new_history[-1][1] = assistant_message

        yield "", new_history

    except Exception as e:
        logger.error(f"Error communicating with MCP server: {e}")
        logger.error(traceback.format_exc())
        error_message = f"Error communicating with the movie recommendation server: {str(e)}"
        new_history[-1][1] = error_message
        yield "", new_history

def update_favorite_genres(genres_text: str) -> str:
    """Update favorite genres in chat state"""
    global chat_state

    logger.info(f"Updating favorite genres: {genres_text}")

    if not genres_text.strip():
        return "No genres specified. Please enter comma-separated genres."

    # Parse genres from comma-separated text
    genres = [genre.strip() for genre in genres_text.split(",")]
    chat_state.favorite_genres = genres

    logger.info(f"Updated favorite genres to: {genres}")
    return f"Updated your favorite genres to: {', '.join(genres)}"

def update_favorite_movies(movies_text: str) -> str:
    """Update favorite movies in chat state"""
    global chat_state

    logger.info(f"Updating favorite movies: {movies_text}")

    if not movies_text.strip():
        return "No movie IDs specified. Please enter comma-separated movie IDs."

    # Parse movie IDs from comma-separated text
    try:
        movie_ids = [int(movie_id.strip()) for movie_id in movies_text.split(",")]
        chat_state.favorite_movies = movie_ids

        logger.info(f"Updated favorite movies to: {movie_ids}")
        return f"Updated your favorite movies to: {', '.join(map(str, movie_ids))}"
    except ValueError:
        logger.error(f"Invalid movie IDs format: {movies_text}")
        return "Invalid input. Please enter comma-separated movie IDs (numbers only)."

def get_popular_movies() -> str:
    """Get popular movies from the MCP server"""
    logger.info("Getting popular movies")

    try:
        response = requests.get(f"{ADMIN_URL}/popular-movies", params={"limit": 10})
        response.raise_for_status()

        result = response.json()
        movies = result.get("movies", [])

        logger.info(f"Retrieved {len(movies)} popular movies")

        if not movies:
            return "No popular movies found."

        return "Here are some popular movies you might enjoy:\n\n" + format_movie_list(movies)
    except Exception as e:
        logger.error(f"Error getting popular movies: {e}")
        logger.error(traceback.format_exc())
        return f"Error getting popular movies: {str(e)}"

def reset_chat_state():
    """Reset the chat state"""
    global chat_state
    logger.info("Resetting chat state")
    chat_state = ChatState()
    return "Chat state has been reset. Your preferences have been cleared."

def initialize_chat():
    """Initialize the chat with a welcome message"""
    logger.info(f"Initializing chat with session ID: {SESSION_ID}")
    return "", [[None, "👋 Welcome to the Movie Recommendation Chat! I can help you find movies based on genres, similar movies, or specific criteria. What kind of movies are you looking for today?"]]

def make_direct_movie_call(movie_id: int) -> str:
    """Make a direct call to get_movie_by_id for debugging"""
    if not movie_id:
        return "Please enter a valid movie ID"

    logger.info(f"Making direct call to get_movie_by_id with ID: {movie_id}")

    try:
        # Try calling the MCP server's tool directly
        url = f"http://localhost:8000/api/mcp/tools/get_movie_by_id"
        response = requests.post(url, json={"movie_id": movie_id})

        # Log the response
        logger.debug(f"Direct call response status: {response.status_code}")
        logger.debug(f"Direct call response: {response.text}")

        if response.status_code == 200:
            movie = response.json()
            return json.dumps(movie, indent=2)
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        logger.error(f"Error in direct movie call: {e}")
        logger.error(traceback.format_exc())
        return f"Error: {str(e)}"

# Create the Gradio interface
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎬 Movie Recommendation Chatbot")
    gr.Markdown("Ask for movie recommendations, search for specific movies, or get information about movies you like.")

    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                height=500,
                bubble_full_width=False,
                avatar_images=(None, "🎬"),
                show_copy_button=True
            )
            msg = gr.Textbox(
                placeholder="Ask for movie recommendations...",
                show_label=False,
                container=False
            )

            with gr.Row():
                clear = gr.Button("🗑️ Clear Chat")
                popular = gr.Button("📊 Show Popular Movies")

        with gr.Column(scale=1):
            gr.Markdown("### User Preferences")

            with gr.Group():
                gr.Markdown("#### Favorite Genres")
                genres_input = gr.Textbox(
                    placeholder="Action, Comedy, Sci-Fi...",
                    label="Enter your favorite genres (comma-separated)"
                )
                update_genres_btn = gr.Button("Update Genres")
                genres_status = gr.Textbox(label="Status", interactive=False)

            with gr.Group():
                gr.Markdown("#### Favorite Movies")
                movies_input = gr.Textbox(
                    placeholder="1, 260, 2571...",
                    label="Enter movie IDs you like (comma-separated)"
                )
                update_movies_btn = gr.Button("Update Movies")
                movies_status = gr.Textbox(label="Status", interactive=False)

            gr.Markdown("### Debug Tools")
            with gr.Group():
                gr.Markdown("#### Direct Movie Lookup")
                debug_movie_id = gr.Number(label="Movie ID", value=1)
                debug_movie_btn = gr.Button("Get Movie Details")
                debug_result = gr.Textbox(label="Result", lines=8)

            reset_btn = gr.Button("Reset Preferences")
            reset_status = gr.Textbox(label="Status", interactive=False, visible=False)

    # Initialize the chat
    demo.load(initialize_chat, outputs=[msg, chatbot])

    # Handle sending messages
    msg.submit(
        send_message_to_mcp,
        [msg, chatbot],
        [msg, chatbot]
    )

    # Button handlers
    clear.click(lambda: ([], ""), outputs=[chatbot, msg])

    popular.click(
        lambda: ([chatbot[-1][0] if len(chatbot) > 0 else None, get_popular_movies()]),
        [],
        [chatbot]
    )

    update_genres_btn.click(
        update_favorite_genres,
        [genres_input],
        [genres_status]
    )

    update_movies_btn.click(
        update_favorite_movies,
        [movies_input],
        [movies_status]
    )

    debug_movie_btn.click(
        make_direct_movie_call,
        [debug_movie_id],
        [debug_result]
    )

    reset_btn.click(
        lambda: (reset_chat_state(), [], ""),
        None,
        [reset_status, chatbot, msg]
    )

# Launch the application
if __name__ == "__main__":
    # Log some startup information
    logger.info("="*50)
    logger.info("Starting Gradio Movie Recommendation Chatbot")
    logger.info(f"Session ID: {SESSION_ID}")
    logger.info(f"MCP Server URL: {MCP_SERVER_URL}")
    logger.info(f"Log file: {os.path.abspath('chatbot_debug.log')}")
    logger.info("="*50)

    demo.launch(server_name="0.0.0.0")