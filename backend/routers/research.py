from fastapi import APIRouter, HTTPException, status
from loguru import logger

from services import task_manager
from services.notebook_repository import notebook_repository
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

@router.post(
    "/audio-overview/{notebook_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate audio overview from notebook summary",
    description="Creates an audio overview using the summary from a completed notebook research. The task runs in the background."
)
async def generate_audio_overview(notebook_id: str):
    """Generate an audio overview from a notebook's research summary."""
    logger.info(f"Generating audio overview for notebook: {notebook_id}")

    # Validate notebook exists
    notebook = await notebook_repository.get_notebook(notebook_id)
    if not notebook:
        logger.warning(f"Notebook not found: {notebook_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notebook not found."
        )

    try:
        # Submit audio overview task
        task_id = await task_manager.submit_audio_overview_task_async(notebook_id)
        logger.info(f"Audio overview task submitted for notebook: {notebook_id}")

        return TaskResponse(
            task_id=task_id,
            notebook_id=notebook_id,
            status="IN_QUEUE",
            message="Audio overview task submitted and will be processed."
        )
    except Exception as e:
        logger.error(f"Error submitting audio overview task for notebook {notebook_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit audio overview task. Please try again."
        )

@router.post(
    "/mindmap/{notebook_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate mindmap from notebook research",
    description="Creates a mindmap structure from the research content in a completed notebook. The task runs in the background."
)
async def generate_mindmap(notebook_id: str):
    """Generate a mindmap from a notebook's research content."""
    logger.info(f"Generating mindmap for notebook: {notebook_id}")

    # Validate notebook exists
    notebook = await notebook_repository.get_notebook(notebook_id)
    if not notebook:
        logger.warning(f"Notebook not found: {notebook_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notebook not found."
        )

    try:
        # Submit mindmap task
        task_id = await task_manager.submit_mindmap_task_async(notebook_id)
        logger.info(f"Mindmap task submitted for notebook: {notebook_id}")

        return TaskResponse(
            task_id=task_id,
            notebook_id=notebook_id,
            status="IN_QUEUE",
            message="Mindmap task submitted and will be processed."
        )
    except Exception as e:
        logger.error(f"Error submitting mindmap task for notebook {notebook_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit mindmap task. Please try again."
        )