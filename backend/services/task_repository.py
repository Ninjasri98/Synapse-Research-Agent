"""
Repository module for task-related database operations.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from sqlalchemy import select, update
from loguru import logger

from models.db import Task
from .db_service import get_db_session

class TaskRepository:
    """Repository for task-related database operations."""

    @staticmethod
    async def create_task(notebook_id: str, topic: Optional[str] = None,
                         sources: Optional[List] = None) -> str:
        """Create a new task in the database.

        Args:
            notebook_id: The notebook ID
            topic: Optional topic for the task
            sources: Optional sources for the task

        Returns:
            str: The ID of the created task
        """
        async with get_db_session() as session:
            task = Task(
                notebook_id=notebook_id,
                topic=topic,
                sources=[source.model_dump() for source in sources] if sources else None,
                status="queued",
                created_at=datetime.now()
            )
            session.add(task)
            await session.commit()
            logger.info(f"Created task {task.id} for notebook {notebook_id}")
            return task.id

    @staticmethod
    async def update_task_status(task_id: str, status: str) -> bool:
        """Update the status of a task.

        Args:
            task_id: The ID of the task
            status: The new status

        Returns:
            bool: True if the task was updated, False otherwise
        """
        async with get_db_session() as session:
            result = await session.execute(
                update(Task)
                .where(Task.id == task_id)
                .values(status=status)
                .returning(Task.id)
            )
            await session.commit()
            updated = result.scalar_one_or_none()
            if updated:
                logger.info(f"Updated task {task_id} status to {status}")
                return True
            logger.warning(f"Failed to update task {task_id} status")
            return False

    @staticmethod
    async def update_task_result(task_id: str, result: Any,
                               status: str = "completed") -> bool:
        """Update the result of a task.

        Args:
            task_id: The ID of the task
            result: The task result
            status: The new status (default: "completed")

        Returns:
            bool: True if the task was updated, False otherwise
        """
        async with get_db_session() as session:
            update_values = {
                "status": status,
                "result": result,
            }

            if status == "completed":
                update_values["completed_at"] = datetime.now()
            elif status == "failed":
                update_values["failed_at"] = datetime.now()

            result = await session.execute(
                update(Task)
                .where(Task.id == task_id)
                .values(**update_values)
                .returning(Task.id)
            )
            await session.commit()
            updated = result.scalar_one_or_none()
            if updated:
                logger.info(f"Updated task {task_id} with result and status {status}")
                return True
            logger.warning(f"Failed to update task {task_id} result")
            return False

    @staticmethod
    async def update_task_error(task_id: str, error: str) -> bool:
        """Update the error of a task.

        Args:
            task_id: The ID of the task
            error: The error message

        Returns:
            bool: True if the task was updated, False otherwise
        """
        async with get_db_session() as session:
            result = await session.execute(
                update(Task)
                .where(Task.id == task_id)
                .values(
                    status="failed",
                    error=error,
                    failed_at=datetime.now()
                )
                .returning(Task.id)
            )
            await session.commit()
            updated = result.scalar_one_or_none()
            if updated:
                logger.info(f"Updated task {task_id} with error")
                return True
            logger.warning(f"Failed to update task {task_id} error")
            return False


# Singleton instance
task_repository = TaskRepository()