from fastapi import APIRouter, HTTPException, status
from loguru import logger

from services import task_manager
from models.task_models import (
    ResearchRequest,
    TaskResponse,
    TaskStatusResponse
)

router = APIRouter(prefix="/research", tags=["research"])

@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit a new research task",
    description="Submits a topic for research. The task runs in the background."
)
async def submit_research_task(request: ResearchRequest):
    logger.info(f"Submitting research task for notebook: {request.notebook_id}" +
              (f" on topic: {request.topic}" if request.topic else ""))

    if not request.notebook_id or request.notebook_id == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Notebook ID is required."
        )

    if (not request.topic or request.topic == "") and (not request.sources or len(request.sources) == 0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either topic or sources must be provided."
        )

    task_id = await task_manager.submit_task_async(
        notebook_id=request.notebook_id,
        topic=request.topic,
        sources=request.sources
    )

    logger.debug(f"Research task submitted with ID: {task_id}")

    return TaskResponse(
        task_id=task_id,
        notebook_id=request.notebook_id,
        status="IN_QUEUE",
        message="Research task submitted and will be processed."
    )

@router.get(
    "/{task_id}",
    response_model=TaskStatusResponse,
    summary="Get research task status by ID",
    description="Retrieves the status and result (if available) of a specific research task."
)
async def get_task_details(task_id: str):
    logger.debug(f"Getting details for task ID: {task_id}")

    # Use the async version to avoid event loop conflicts
    task_info = await task_manager.get_task_status_async(task_id)

    if not task_info:
        logger.warning(f"Task not found: {task_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found."
        )
    return TaskStatusResponse(**task_info, task_id=task_id)
