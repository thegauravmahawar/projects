from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from datetime import datetime

class MessageRole(str, Enum):
    """Roles for chat messages"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"

class Message(BaseModel):
    """Chat message model"""
    role: MessageRole
    content: str
    name: Optional[str] = None

class FunctionCall(BaseModel):
    """Function call model"""
    name: str
    arguments: Dict[str, Any]

class FunctionDefinition(BaseModel):
    """Function definition model"""
    name: str
    description: str
    parameters: Dict[str, Any]

class FunctionResponse(BaseModel):
    """Function response model"""
    name: str
    content: Any

class MCPContext(BaseModel):
    """Context information for MCP request"""
    user_id: Optional[str] = None
    session_id: str
    favorite_genres: Optional[List[str]] = None
    favorite_movies: Optional[List[int]] = None
    recent_searches: Optional[List[str]] = None

class MCPRequest(BaseModel):
    """MCP request model"""
    messages: List[Message]
    context: MCPContext
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False

class MCPResponse(BaseModel):
    """MCP response model"""
    message: Message
    function_call: Optional[FunctionCall] = None
    context_update: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.now)