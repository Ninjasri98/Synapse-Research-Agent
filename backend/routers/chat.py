from fastapi import APIRouter, status, HTTPException
from loguru import logger
from models.chat_models import ChatMessageInput
from agents.chat_agent import run_chat_agent

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/message", status_code=status.HTTP_201_CREATED)
async def receive_chat_message(chat_input: ChatMessageInput):
    """
    Endpoint to receive a new chat message

    Args:
        chat_input: The chat message data including list of messages and notebook ID

    Returns:
        dict: A response with message details and status
    """
    try:
        logger.info(f"Received chat message for notebook: {chat_input.notebook_id}")

        response = await run_chat_agent(chat_input.notebook_id, chat_input.messages)

        return {
            "status": "success",
            "response": response,
        }
    except Exception as e:
        logger.opt(exception=e).error(f"Error processing chat message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message"
        )

