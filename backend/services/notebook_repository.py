"""
Notebook repository service for database operations.

This module provides methods for creating, retrieving, and updating notebooks.
"""

from typing import Optional, Dict, Any, List
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

    async def save_notebook_sources(self, notebook_id: str, sources: List[Dict[str, Any]]) -> None:
        """
        Save or update notebook sources.

        Args:
            notebook_id: The notebook ID
            sources: List of source dictionaries
        """
        async with get_db_session() as session:
            # Create new source entries
            new_sources = [
                NotebookSource(
                    notebook_id=notebook_id,
                    source_type=NotebookDocumentSourceType.URL,
                    source_url=source["url"],
                    source_url_text=source["page_title"],
                    content=source["content"],
                    created_at=datetime.now()
                )
                for source in sources
            ]
            session.add_all(new_sources)

            # Update notebook updated_at timestamp
            notebook_stmt = update(Notebook).where(
                Notebook.id == notebook_id
            ).values(updated_at=datetime.now())
            await session.execute(notebook_stmt)

            await session.commit()
            logger.info(f"Saved {len(new_sources)} sources for notebook {notebook_id}")

    async def get_notebook(self, notebook_id: str) -> Optional[Dict[str, Any]]:
        """
        Get notebook details.

        Args:
            notebook_id: The notebook ID

        Returns:
            Dict with notebook details or None if not found
        """
        async with get_db_session() as session:
            stmt = select(Notebook).where(Notebook.id == notebook_id)
            result = await session.execute(stmt)
            notebook = result.scalar_one_or_none()

            if not notebook:
                return None

            return notebook.to_dict()

    async def get_notebook_output(self, notebook_id: str) -> Optional[str]:
        """
        Get notebook output summary.

        Args:
            notebook_id: The notebook ID

        Returns:
            The summary string or None if not found
        """
        async with get_db_session() as session:
            stmt = select(NotebookOutput).where(NotebookOutput.notebook_id == notebook_id)
            result = await session.execute(stmt)
            notebook_output = result.scalar_one_or_none()

            if not notebook_output:
                return None

            return notebook_output.summary

    async def update_notebook(
        self,
        notebook_id: str,
        title: Optional[str] = None,
        topic: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update an existing notebook.

        Args:
            notebook_id: The ID of the notebook to update.
            title: Optional new title for the notebook.
            topic: Optional new topic for the notebook.

        Returns:
            A dictionary representation of the updated notebook, or None if not found.
        """
        async with get_db_session() as session:
            stmt = select(Notebook).where(Notebook.id == notebook_id)
            result = await session.execute(stmt)
            notebook = result.scalar_one_or_none()

            if not notebook:
                logger.warning(f"Notebook with ID {notebook_id} not found for update.")
                return None

            updated_fields = False
            if title is not None:
                notebook.title = title
                updated_fields = True

            if topic is not None:
                notebook.topic = topic
                updated_fields = True

            if updated_fields:
                notebook.updated_at = datetime.now() # Manually update timestamp as onupdate might not trigger for all ORM scenarios
                await session.commit()
                await session.refresh(notebook)
                logger.info(f"Updated notebook with ID: {notebook.id}")
            else:
                logger.info(f"No fields to update for notebook with ID: {notebook.id}")

            return notebook.to_dict()

    async def delete_notebook_faqs(self, notebook_id: str) -> None:
        """
        Delete all FAQs for a specific notebook.

        Args:
            notebook_id: The notebook ID to delete FAQs for
        """
        async with get_db_session() as session:
            # Get the notebook output ID
            stmt = select(NotebookOutput).where(NotebookOutput.notebook_id == notebook_id)
            result = await session.execute(stmt)
            notebook_output = result.scalar_one_or_none()

            if notebook_output:
                # Delete all FAQs associated with this notebook output
                stmt = select(NotebookFAQ).where(NotebookFAQ.notebook_output_id == notebook_output.id)
                result = await session.execute(stmt)
                faqs = result.scalars().all()

                for faq in faqs:
                    await session.delete(faq)

                await session.commit()
                logger.info(f"Deleted {len(faqs)} FAQs for notebook {notebook_id}")
            else:
                logger.info(f"No FAQs found for notebook {notebook_id}")

    async def save_notebook_faqs(self, notebook_id: str, faqs: List[Dict[str, str]]) -> None:
        """
        Save or update FAQs for a notebook.

        Args:
            notebook_id: The notebook ID
            faqs: List of FAQ dictionaries with 'question' and 'answer' keys
        """
        async with get_db_session() as session:
            # Get the notebook output
            stmt = select(NotebookOutput).where(
                NotebookOutput.notebook_id == notebook_id
            )
            result = await session.execute(stmt)
            notebook_output = result.scalar_one_or_none()

            if not notebook_output:
                logger.warning(f"No notebook output found for notebook {notebook_id}")
                return

            # Create new FAQ entries
            new_faqs = [
                NotebookFAQ(
                    question=faq["question"],
                    answer=faq["answer"],
                    notebook_output_id=notebook_output.id,
                    created_at=datetime.now()
                )
                for faq in faqs
            ]
            session.add_all(new_faqs)

            # Update notebook updated_at timestamp
            notebook_stmt = update(Notebook).where(
                Notebook.id == notebook_id
            ).values(updated_at=datetime.now())
            await session.execute(notebook_stmt)

            await session.commit()
            logger.info(f"Saved {len(new_faqs)} FAQs for notebook {notebook_id}")

    async def update_audio_overview_url(self, notebook_id: str, audio_url: str) -> None:
        """
        Update the audio overview URL for a notebook output.

        Args:
            notebook_id: The notebook ID
            audio_url: The URL of the uploaded audio file
        """
        async with get_db_session() as session:
            # Get the notebook output
            stmt = select(NotebookOutput).where(
                NotebookOutput.notebook_id == notebook_id
            )
            result = await session.execute(stmt)
            notebook_output = result.scalar_one_or_none()

            if not notebook_output:
                logger.warning(f"No notebook output found for notebook {notebook_id}")
                return

            # Update the audio overview URL
            notebook_output.audio_overview_url = audio_url

            # Update notebook updated_at timestamp
            notebook_stmt = update(Notebook).where(
                Notebook.id == notebook_id
            ).values(updated_at=datetime.now())
            await session.execute(notebook_stmt)

            await session.commit()
            logger.info(f"Updated audio overview URL for notebook {notebook_id}")

    async def update_notebook_mindmap(self, notebook_id: str, mindmap: Dict[str, Any]) -> None:
        """
        Update the mindmap for a notebook output.

        Args:
            notebook_id: The notebook ID
            mindmap: The mindmap structure as a nested dictionary
        """
        async with get_db_session() as session:
            # Get the notebook output
            stmt = select(NotebookOutput).where(
                NotebookOutput.notebook_id == notebook_id
            )
            result = await session.execute(stmt)
            notebook_output = result.scalar_one_or_none()

            if not notebook_output:
                logger.warning(f"No notebook output found for notebook {notebook_id}")
                return

            # Update the mindmap
            notebook_output.mindmap = mindmap

            # Update notebook updated_at timestamp
            notebook_stmt = update(Notebook).where(
                Notebook.id == notebook_id
            ).values(updated_at=datetime.now())
            await session.execute(notebook_stmt)

            await session.commit()
            logger.info(f"Updated mindmap for notebook {notebook_id}")

# Singleton instance
notebook_repository = NotebookRepository()