from typing import Optional, List
from loguru import logger

from agents import topic_research_agent, sources_research_agent
from models.db import NotebookProcessingStatusValue
from .task_repository import task_repository
from .notebook_repository import notebook_repository
from .qdrant_service import qdrant_service

class TaskManager:
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
