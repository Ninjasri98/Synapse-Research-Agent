"""
Notebook repository service for database operations.

This module provides methods for creating, retrieving, and updating notebooks.
"""

from typing import Optional
from datetime import datetime
from loguru import logger

from sqlalchemy import select, update

from models.db import Notebook, NotebookProcessingStatus, NotebookOutput, NotebookProcessingStatusValue, NotebookSource, NotebookDocumentSourceType, NotebookFAQ
from services.db_service import get_db_session

class NotebookRepository:
    """Repository for notebook database operations."""

    async def update_notebook_status(
        self,
        notebook_id: str,
        status: NotebookProcessingStatusValue,
        message: Optional[str] = None
    ) -> None:
        """
        Update notebook processing status.

        Args:
            notebook_id: The notebook ID
            status: The new status
            message: Optional status message
        """
        async with get_db_session() as session:
            # Check if a status entry exists
            stmt = select(NotebookProcessingStatus).where(
                NotebookProcessingStatus.notebook_id == notebook_id
            )
            result = await session.execute(stmt)
            processing_status = result.scalar_one_or_none()

            if processing_status:
                # Update existing status
                processing_status.status = status
                if message:
                    processing_status.message = message
                processing_status.updated_at = datetime.now()
            else:
                # Create new status entry
                new_status = NotebookProcessingStatus(
                    notebook_id=notebook_id,
                    status=status,
                    message=message
                )
                session.add(new_status)

            # Update notebook updated_at timestamp
            notebook_stmt = update(Notebook).where(
                Notebook.id == notebook_id
            ).values(updated_at=datetime.now())
            await session.execute(notebook_stmt)

            await session.commit()
            logger.info(f"Updated notebook {notebook_id} status to {status}")

    async def save_notebook_output(self, notebook_id: str, summary: str) -> None:
        """
        Save or update notebook output summary.

        Args:
            notebook_id: The notebook ID
            summary: The research summary text
        """
        async with get_db_session() as session:
            # Check if output already exists
            stmt = select(NotebookOutput).where(
                NotebookOutput.notebook_id == notebook_id
            )
            result = await session.execute(stmt)
            notebook_output = result.scalar_one_or_none()

            if notebook_output:
                # Update existing output
                notebook_output.summary = summary
            else:
                # Create new output entry
                new_output = NotebookOutput(
                    notebook_id=notebook_id,
                    summary=summary
                )
                session.add(new_output)

            # Update notebook updated_at timestamp
            notebook_stmt = update(Notebook).where(
                Notebook.id == notebook_id
            ).values(updated_at=datetime.now())
            await session.execute(notebook_stmt)

            await session.commit()
            logger.info(f"Saved output summary for notebook {notebook_id}")
