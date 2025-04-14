import gradio as gr
import requests
import uuid
import json
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MCP Server connection settings
MCP_SERVER_URL = "http://localhost:8000/api/mcp/chat"
SESSION_ID = str(uuid.uuid4())  # Generate a session ID for this chat instance

# History of messages for context
message_history = []

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

def send_message_to_mcp(message: str, history: List[List[str]]) -> str:
    """Send a message to the MCP server and get a response"""
    global message_history

    # Prepare the request payload
    mcp_messages = []

    # Add history to provide context (excluding system messages)
    for human_msg, ai_msg in history:
        mcp_messages.append({"role": "user", "content": human_msg})
        mcp_messages.append({"role": "assistant", "content": ai_msg})

    # Add the current message
    mcp_messages.append({"role": "user", "content": message})

    # Store in our history
    message_history = mcp_messages

    # Prepare the request payload
    payload = {
        "messages": mcp_messages,
        "context": {
            "session_id": SESSION_ID,
            "favorite_genres": []  # You can customize this based on user preferences
        }
    }

    try:
        # Send the request to the MCP server
        logger.info(f"Sending request to MCP server: {payload}")
        response = requests.post(MCP_SERVER_URL, json=payload)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses

        mcp_response = response.json()
        logger.info(f"Received response from MCP server: {mcp_response}")

        # Extract the assistant's message
        assistant_message = mcp_response.get("message", {}).get("content", "")

        # Check if there was a function call
        function_call = mcp_response.get("function_call")
        if function_call:
            function_name = function_call.get("name", "")
            arguments = function_call.get("arguments", {})

            function_info = f"\n\n*Used function: {function_name} with arguments: {json.dumps(arguments, indent=2)}*"
            return assistant_message

        return assistant_message

    except Exception as e:
        logger.error(f"Error communicating with MCP server: {e}")
        return f"Error communicating with the movie recommendation server: {str(e)}"

def initialize_chat():
    """Initialize the chat with a welcome message"""
    return "", [[None, "👋 Welcome to the Movie Recommendation Chat! I can help you find movies based on genres, similar movies, or specific criteria. What kind of movies are you looking for today?"]]

# Create the Gradio interface
with gr.Blocks(css="footer {visibility: hidden}") as demo:
    gr.Markdown("# 🎬 Movie Recommendation Chatbot")
    gr.Markdown("Ask for movie recommendations, search for specific movies, or get information about movies you like.")

    chatbot = gr.Chatbot(height=500)
    msg = gr.Textbox(placeholder="Ask for movie recommendations...", show_label=False)
    clear = gr.Button("Clear Conversation")

    # Initialize the chat
    demo.load(initialize_chat, outputs=[msg, chatbot])

    # Handle sending messages
    msg.submit(
        send_message_to_mcp,
        [msg, chatbot],
        [msg, chatbot],
        postprocess=lambda msg, history: ("", history + [[msg, send_message_to_mcp(msg, history)]])
    )

    # Clear the chat history
    clear.click(lambda: ([], ""), outputs=[chatbot, msg])
    clear.click(lambda: [], outputs=[chatbot])

# Launch the application
if __name__ == "__main__":
    demo.launch(share=False, server_name="0.0.0.0")