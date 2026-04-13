import asyncio
from typing import Dict, Optional, List, Any
from loguru import logger
from sqlalchemy import select

from agents import topic_research_agent, sources_research_agent
from models.db import NotebookProcessingStatusValue, Task
from .task_repository import task_repository
from .notebook_repository import notebook_repository
from .qdrant_service import qdrant_service
from .audio_overview_service import audio_overview_service
from .db_service import get_db_session

class TaskManager:

    async def _delete_notebook_data(self, notebook_id: str) -> None:
        """Delete FAQs and embeddings for a notebook.

        Args:
            notebook_id: The ID of the notebook to delete data for.
        """
        try:
            # Delete faqs from db
            logger.info(f"Deleting existing FAQs for notebook: {notebook_id}")
            await notebook_repository.delete_notebook_faqs(notebook_id)

            # Delete embeddings from qdrant
            logger.info(f"Deleting existing embeddings for notebook: {notebook_id}")
            await qdrant_service.delete_by_notebook_id(notebook_id)
        except Exception as e:
            logger.error(f"Error deleting existing FAQs and embeddings for notebook: {notebook_id}")
            logger.error(e)

    async def _execute_task(self, task_id: str, topic: Optional[str], notebook_id: str, sources: Optional[List] = None):
        """Internal method to run the research task and update status."""
        max_retries = 1
        retry_count = 0

        await notebook_repository.update_notebook_status(
            notebook_id,
            NotebookProcessingStatusValue.IN_PROGRESS,
            "Research task started"
        )

        while retry_count < max_retries:
            try:

                await task_repository.update_task_status(task_id, "running")

                logger.info(f"Task {task_id} started for notebook: {notebook_id}" +
                           (f" on topic: {topic}" if topic else "") +
                           (f" (retry {retry_count}/{max_retries-1})" if retry_count > 0 else ""))

                with logger.contextualize(task_id=task_id):
                    if topic and topic != "" and (not sources or len(sources) == 0):
                        # Run topic research agent
                        logger.info(f"Running topic research agent for topic: {topic}")
                        result = await topic_research_agent.run_research_crew(topic)
                        # Save notebook output
                        logger.info(f"Saving notebook output for notebook: {notebook_id}")
                        await notebook_repository.save_notebook_output(notebook_id, result["blog_post"])

                        # Update notebook title and topic
                        logger.info(f"Updating notebook title and topic for notebook: {notebook_id}")
                        title = result["title"]
                        await notebook_repository.update_notebook(
                            notebook_id,
                            title=title,
                            topic=topic
                        )

                        await self._delete_notebook_data(notebook_id)

                        # Save faqs in db
                        await notebook_repository.save_notebook_faqs(notebook_id, result["faq"])
                        # Save embeddings for blog post
                        max_embedding_retries = 3
                        embedding_retry_count = 0

                        while embedding_retry_count < max_embedding_retries:
                            try:
                                # Save sources in Qdrant
                                logger.info(f"Embedding blog post for notebook: {notebook_id} (attempt {embedding_retry_count + 1}/{max_embedding_retries})")
                                await qdrant_service.add_source(
                                    content=result["blog_post"],
                                    notebook_id=notebook_id,
                                    metadata={
                                        "title": result["title"],
                                    }
                                )

                                logger.info(f"Embedding scraped data for notebook: {notebook_id} (attempt {embedding_retry_count + 1}/{max_embedding_retries})")
                                for source in result["scraped_data"]:
                                    await qdrant_service.add_source(
                                        content=source["content"],
                                        notebook_id=notebook_id,
                                        metadata={
                                            "url": source["url"],
                                            "page_title": source["page_title"],
                                        }
                                    )
                                break  # Success - exit retry loop

                            except Exception as e:
                                embedding_retry_count += 1
                                if embedding_retry_count < max_embedding_retries:
                                    logger.warning(f"Error embedding sources for notebook: {notebook_id} (attempt {embedding_retry_count}/{max_embedding_retries})")
                                    logger.warning(e)
                                    continue
                                logger.error(f"Error embedding sources for notebook: {notebook_id} after {max_embedding_retries} attempts")
                                logger.error(e)


                    elif  sources and len(sources) > 0:
                        # Run sources research agent
                        logger.info(f"Running sources research agent for sources: {sources}")
                        result = await sources_research_agent.run_sources_research_crew(sources)
                        # Save notebook output
                        logger.info(f"Saving notebook output for notebook: {notebook_id}")
                        await notebook_repository.save_notebook_output(notebook_id, result["blog_post"])

                        # Update notebook title and topic
                        logger.info(f"Updating notebook title and topic for notebook: {notebook_id}")
                        title = result["title"]
                        await notebook_repository.update_notebook(
                            notebook_id,
                            title=title
                        )

                        await self._delete_notebook_data(notebook_id)

                        # Save faqs in db
                        await notebook_repository.save_notebook_faqs(notebook_id, result["faq"])

                        max_embedding_retries = 3
                        embedding_retry_count = 0

                        while embedding_retry_count < max_embedding_retries:
                            try:
                                # Save textual content in Qdrant
                                logger.info(f"Embedding textual content for notebook: {notebook_id} (attempt {embedding_retry_count + 1}/{max_embedding_retries})")

                                for source in sources:
                                    if source.source_type == "MANUAL":
                                        await qdrant_service.add_source(
                                            content=source.source_content,
                                            notebook_id=notebook_id
                                        )

                                # Save file content in Qdrant
                                logger.info(f"Embedding file content for notebook: {notebook_id} (attempt {embedding_retry_count + 1}/{max_embedding_retries})")
                                for file_data in result["file_data"]:
                                    await qdrant_service.add_source(
                                        content=file_data["content"],
                                        notebook_id=notebook_id,
                                        metadata={
                                            "url": file_data["file_name"]
                                        }
                                    )

                                # Save sources in Qdrant
                                logger.info(f"Embedding blog post for notebook: {notebook_id} (attempt {embedding_retry_count + 1}/{max_embedding_retries})")
                                await qdrant_service.add_source(
                                    content=result["blog_post"],
                                    notebook_id=notebook_id,
                                    metadata={
                                        "title": result["title"],
                                    }
                                )

                                logger.info(f"Embedding scraped data for notebook: {notebook_id} (attempt {embedding_retry_count + 1}/{max_embedding_retries})")
                                for source in result["scraped_data"]:
                                    await qdrant_service.add_source(
                                        content=source["content"],
                                        notebook_id=notebook_id,
                                        metadata={
                                            "url": source["url"]
                                        }
                                    )

                                break

                            except Exception as e:
                                embedding_retry_count += 1
                                if embedding_retry_count < max_embedding_retries:
                                    logger.warning(f"Error embedding sources for notebook: {notebook_id} (attempt {embedding_retry_count}/{max_embedding_retries})")
                                    logger.warning(e)
                                    continue
                                logger.error(f"Error embedding sources for notebook: {notebook_id} after {max_embedding_retries} attempts")
                                logger.error(e)
                    else:
                        logger.error("Not supported research type")
                        return


                await task_repository.update_task_result(task_id, result, "completed")

                await notebook_repository.update_notebook_status(
                    notebook_id,
                    NotebookProcessingStatusValue.PROCESSED,
                    "Research completed successfully"
                )

                logger.success(f"Task {task_id} completed successfully")
                return

            except Exception as e:
                retry_count += 1
                # Log the error but keep retrying if we haven't hit the limit
                if retry_count < max_retries:
                    logger.warning(f"Task {task_id} failed (attempt {retry_count}/{max_retries-1}): {e}")
                    continue

                logger.opt(exception=True).error(f"Task {task_id} failed after {retry_count} attempts: {e}")

                await task_repository.update_task_error(task_id, str(e))

                await notebook_repository.update_notebook_status(
                    notebook_id,
                    NotebookProcessingStatusValue.ERROR,
                    f"Research failed. Please try again."
                )

                return

    async def submit_task_async(self, notebook_id: str, topic: Optional[str] = None, sources: Optional[List] = None) -> str:
        """Async implementation for submitting a new research task."""

        task_id = await task_repository.create_task(notebook_id, topic, sources)

        asyncio.create_task(self._execute_task(task_id, topic, notebook_id, sources))

        logger.info(f"Task {task_id} submitted for notebook: {notebook_id}" + (f" on topic: {topic}" if topic else ""))
        return task_id

    async def _execute_audio_overview_task(self, task_id: str, notebook_id: str):
        """Internal method to run the audio overview task and update status."""

        max_retries = 1
        retry_count = 0

        while retry_count < max_retries:
            try:
                await task_repository.update_task_status(task_id, "running")

                logger.info(f"Audio overview task {task_id} started for notebook: {notebook_id}" +
                           (f" (retry {retry_count}/{max_retries-1})" if retry_count > 0 else ""))

                with logger.contextualize(task_id=task_id):

                    # Update database with audio URL - IN_PROGRESS
                    logger.info(f"Updating database with audio URL - IN_PROGRESS for notebook: {notebook_id}")
                    await notebook_repository.update_audio_overview_url(notebook_id, "IN_PROGRESS")

                    # Generate complete audio overview
                    result = await audio_overview_service.generate_complete_audio_overview(notebook_id)

                await task_repository.update_task_result(task_id, result, "completed")

                logger.success(f"Audio overview task {task_id} completed successfully")
                return

            except Exception as e:
                retry_count += 1
                # Log the error but keep retrying if we haven't hit the limit
                if retry_count < max_retries:
                    logger.warning(f"Audio overview task {task_id} failed (attempt {retry_count}/{max_retries-1}): {e}")
                    continue

                logger.opt(exception=True).error(f"Audio overview task {task_id} failed after {retry_count} attempts: {e}")

                await task_repository.update_task_error(task_id, str(e))

                # Update database with audio URL - ERROR
                logger.info(f"Updating database with audio URL - ERROR for notebook: {notebook_id}")
                await notebook_repository.update_audio_overview_url(notebook_id, "ERROR")

                return

    async def submit_audio_overview_task_async(self, notebook_id: str) -> str:
        """Async implementation for submitting a new audio overview task."""

        task_id = await task_repository.create_task(notebook_id, topic="audio_overview")

        asyncio.create_task(self._execute_audio_overview_task(task_id, notebook_id))

        logger.info(f"Audio overview task {task_id} submitted for notebook: {notebook_id}")
        return task_id

    async def _execute_mindmap_task(self, task_id: str, notebook_id: str):
        """Internal method to run the mindmap task and update status."""

        max_retries = 1
        retry_count = 0

        while retry_count < max_retries:
            try:
                await task_repository.update_task_status(task_id, "running")

                logger.info(f"Mindmap task {task_id} started for notebook: {notebook_id}" +
                           (f" (retry {retry_count}/{max_retries-1})" if retry_count > 0 else ""))

                with logger.contextualize(task_id=task_id):
                    # Import here to avoid circular imports
                    from agents.mindmap_agent import run_mindmap_agent

                    # Generate mindmap structure
                    result = await run_mindmap_agent(notebook_id)

                    # Save mindmap to notebook output
                    logger.info(f"Saving mindmap to database for notebook: {notebook_id}")
                    await notebook_repository.update_notebook_mindmap(notebook_id, result)

                await task_repository.update_task_result(task_id, result, "completed")

                logger.success(f"Mindmap task {task_id} completed successfully")
                return

            except Exception as e:
                retry_count += 1
                # Log the error but keep retrying if we haven't hit the limit
                if retry_count < max_retries:
                    logger.warning(f"Mindmap task {task_id} failed (attempt {retry_count}/{max_retries-1}): {e}")
                    continue

                logger.opt(exception=True).error(f"Mindmap task {task_id} failed after {retry_count} attempts: {e}")

                await task_repository.update_task_error(task_id, str(e))

                # Save mindmap to notebook output
                logger.info(f"Saving mindmap to database for notebook: {notebook_id}")
                await notebook_repository.update_notebook_mindmap(notebook_id, "ERROR")

                return

    async def submit_mindmap_task_async(self, notebook_id: str) -> str:
        """Async implementation for submitting a new mindmap task."""

        task_id = await task_repository.create_task(notebook_id, topic="mindmap")

        asyncio.create_task(self._execute_mindmap_task(task_id, notebook_id))

        logger.info(f"Mindmap task {task_id} submitted for notebook: {notebook_id}")
        return task_id

    async def get_task_status_async(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status and details by task ID."""
        async with get_db_session() as session:
            stmt = select(Task).where(Task.id == task_id)
            result = await session.execute(stmt)
            task = result.scalar_one_or_none()

            if not task:
                return None

            return {
                "notebook_id": task.notebook_id,
                "topic": task.topic,
                "status": task.status,
                "result": task.result,
                "error": task.error,
                "created_at": task.created_at,
                "completed_at": task.completed_at,
                "failed_at": task.failed_at
            }

# Singleton instance
task_manager = TaskManager()