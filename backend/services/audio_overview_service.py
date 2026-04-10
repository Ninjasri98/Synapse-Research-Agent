"""
Audio overview service that orchestrates TTS generation, file upload, and database updates.
"""

import asyncio
from typing import Dict, Any
from loguru import logger

from agents.audio_overview_agent import run_audio_overview_agent
from .tts_service import tts_service
from .r2_service import r2_service
from .notebook_repository import notebook_repository


class AudioOverviewService:
    """Service for generating complete audio overviews from notebook content."""

    async def generate_complete_audio_overview(self, notebook_id: str) -> Dict[str, Any]:
        """
        Generate a complete audio overview including transcript, TTS, upload, and database update.

        Args:
            notebook_id: The notebook ID to generate audio overview for

        Returns:
            Dictionary with transcript and audio URL
        """
        logger.info(f"Starting complete audio overview generation for notebook: {notebook_id}")

        try:
            # Step 1: Generate transcript using the audio overview agent
            logger.info(f"Generating transcript for notebook: {notebook_id}")
            transcript = await run_audio_overview_agent(notebook_id)

            # Step 2: Generate TTS audio from transcript
            logger.info(f"Generating TTS audio for notebook: {notebook_id}")
            audio_content = await tts_service.generate_audio_from_transcript(
                transcript, notebook_id
            )

            # Step 3: Upload audio file to R2
            logger.info(f"Uploading audio file to R2 for notebook: {notebook_id}")
            audio_url = await r2_service.upload_audio_file(
                audio_content, notebook_id
            )

            # Step 4: Update database with audio URL
            logger.info(f"Updating database with audio URL {audio_url} for notebook: {notebook_id}")
            await notebook_repository.update_audio_overview_url(notebook_id, audio_url)

            logger.success(f"Complete audio overview generation completed for notebook: {notebook_id} URL: {audio_url}")

            return {
                "transcript": transcript,
                "audio_url": audio_url,
                "status": "completed"
            }

        except Exception as e:
            error_msg = f"Failed to generate complete audio overview for notebook {notebook_id}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)


# Singleton instance
audio_overview_service = AudioOverviewService()