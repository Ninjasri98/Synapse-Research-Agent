"""
Text-to-Speech service using LemonFox AI API.
Optimized for memory efficiency and async performance.
"""

import os
import io
import asyncio
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional
import httpx
from loguru import logger
from pydub import AudioSegment


class TTSService:
    """Service for converting text to speech using LemonFox AI API."""

    def __init__(self):
        self.api_key = os.environ.get("LEMONFOX_API_KEY")
        if not self.api_key:
            raise ValueError("LEMONFOX_API_KEY environment variable is required")

        self.base_url = "https://api.lemonfox.ai/v1/audio/speech"
        self.response_format = "mp3"

        # Voice mapping for different speakers
        self.speaker_voices = {
            "Michael": "liam",    # Host voice
            "Sarah": "jessica"  # Guest voice
        }

        # Pause duration between segments (in milliseconds)
        self.pause_duration = 500  # 0.5 seconds

        # Connection pool for reusing HTTP connections
        self._client: Optional[httpx.AsyncClient] = None
        self._client_lock = asyncio.Lock()

        # Concurrency settings
        self.max_concurrent_requests = 5
        self.semaphore = asyncio.Semaphore(self.max_concurrent_requests)

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client with connection pooling."""
        if self._client is None or self._client.is_closed:
            async with self._client_lock:
                if self._client is None or self._client.is_closed:
                    # Configure connection limits for optimal performance
                    limits = httpx.Limits(
                        max_keepalive_connections=10,
                        max_connections=20,
                        keepalive_expiry=30.0
                    )
                    self._client = httpx.AsyncClient(
                        timeout=httpx.Timeout(300.0),  # 5 minute timeout
                        limits=limits,
                        http2=True  # Enable HTTP/2 for better performance
                    )
        return self._client

    async def close(self):
        """Close the HTTP client and cleanup resources."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    @asynccontextmanager
    async def _audio_segment_context(self, audio_bytes: bytes):
        """Context manager for AudioSegment to ensure proper cleanup."""
        audio_buffer = None
        audio_segment = None
        try:
            audio_buffer = io.BytesIO(audio_bytes)
            audio_segment = AudioSegment.from_mp3(audio_buffer)
            yield audio_segment
        finally:
            # Explicit cleanup
            if audio_buffer:
                audio_buffer.close()
            # AudioSegment doesn't need explicit cleanup, but we clear the reference
            del audio_segment

    async def generate_audio_from_transcript(
        self,
        transcript: List[Dict[str, Any]],
        notebook_id: str
    ) -> bytes:
        """
        Generate audio from transcript segments with different voices per speaker.
        Optimized for memory efficiency and concurrent processing.

        Args:
            transcript: List of transcript segments with 'name' and 'transcript' fields
            notebook_id: The notebook ID for logging purposes

        Returns:
            Combined audio file content as bytes
        """
        logger.info(f"Generating TTS audio for notebook: {notebook_id}")

        # Filter out empty segments early
        valid_segments = [
            (i, segment) for i, segment in enumerate(transcript)
            if segment.get("transcript", "").strip()
        ]

        if not valid_segments:
            raise Exception("No valid text segments found in transcript")

        try:
            # Process segments concurrently with semaphore for rate limiting
            tasks = []
            for i, segment in valid_segments:
                speaker = segment.get("name", "Michael")
                text = segment.get("transcript", "")
                voice = self.speaker_voices.get(speaker, "jessica")

                task = self._generate_audio_with_semaphore(text, voice, i + 1, len(transcript))
                tasks.append(task)

            # Execute all TTS requests concurrently
            logger.info(f"Processing {len(tasks)} segments concurrently (max {self.max_concurrent_requests} at a time)")
            audio_bytes_list = await asyncio.gather(*tasks, return_exceptions=True)

            # Check for exceptions
            for i, result in enumerate(audio_bytes_list):
                if isinstance(result, Exception):
                    logger.error(f"Failed to generate audio for segment {i + 1}: {result}")
                    raise result

            # Combine audio segments efficiently
            return await self._combine_audio_segments(audio_bytes_list, valid_segments)

        except Exception as e:
            logger.error(f"Failed to generate TTS audio for notebook {notebook_id}: {e}")
            raise
