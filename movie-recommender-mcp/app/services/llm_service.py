import logging
import json
import os
from typing import List, Dict, Any, Optional, Union
import requests
import aiohttp
import asyncio

from app.config import settings
from app.models.mcp_models import Message, MessageRole, FunctionCall, FunctionDefinition

logger = logging.getLogger(__name__)

async def call_llm(
    messages: List[Message],
    functions: Optional[List[FunctionDefinition]] = None,
    function_call: Optional[str] = "auto",
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    stream: bool = False
) -> Dict[str, Any]:
    """
    Call the LLM API with the given messages and optional functions

    Args:
        messages: List of messages to send to the LLM
        functions: List of function definitions
        function_call: Control when the model calls functions
        temperature: Temperature for response generation
        max_tokens: Maximum number of tokens in the response
        stream: Whether to stream the response

    Returns:
        LLM API response
    """
    if not settings.LLM_API_KEY:
        raise ValueError("LLM_API_KEY is not set")

    # Use default settings if not specified
    temperature = temperature if temperature is not None else settings.LLM_TEMPERATURE
    max_tokens = max_tokens if max_tokens is not None else settings.LLM_MAX_TOKENS

    # Convert Message objects to dictionaries
    message_dicts = [
        {
            "role": message.role.value,
            "content": message.content,
            **({"name": message.name} if message.name else {})
        }
        for message in messages
    ]

    # Convert function definitions to the format expected by the LLM API
    function_dicts = None
    if functions:
        function_dicts = [
            {
                "name": func.name,
                "description": func.description,
                "parameters": func.parameters
            }
            for func in functions
        ]

    # Use OpenAI API format
    return await _call_openai_api(message_dicts, function_dicts, function_call, temperature, max_tokens)

async def _call_openai_api(
    messages: List[Dict[str, Any]],
    functions: Optional[List[Dict[str, Any]]] = None,
    function_call: Optional[str] = "auto",
    temperature: float = 0.7,
    max_tokens: int = 1000
) -> Dict[str, Any]:
    """Call the OpenAI API"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.LLM_API_KEY}"
    }

    payload = {
        "model": settings.LLM_MODEL_NAME,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    # Add functions if provided
    if functions:
        payload["functions"] = functions
        payload["function_call"] = function_call

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {e}")
        raise