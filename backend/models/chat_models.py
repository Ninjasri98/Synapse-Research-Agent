from pydantic import BaseModel, Field
from typing import Optional, List

class ChatMessage(BaseModel):
    role: str = Field(..., description="The role of the message sender")
    content: str = Field(..., description="The content of the message")

class ChatMessageInput(BaseModel):
    """Schema for chat message input"""
    messages: List[ChatMessage] = Field(..., description="The chat messages")
    notebook_id: str = Field(..., description="The ID of the notebook this message belongs to")
    metadata: Optional[dict] = Field(default=None, description="Additional metadata for the message")
