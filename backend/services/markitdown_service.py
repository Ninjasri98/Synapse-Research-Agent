import asyncio
import os
import tempfile
from typing import Dict, List, Optional, Tuple

import aiohttp
from loguru import logger
from markitdown import MarkItDown


class MarkdownConversionError(Exception):
    """Custom exception for Markdown conversion failures."""
    pass


class MarkdownConverter:
    """
    Asynchronous Markdown converter service for converting files from URLs.

    Downloads files from URLs and converts them to Markdown using MarkItDown,
    returning the markdown content directly.
    """

    def __init__(
        self,
        timeout: int = 60,
        retries: int = 3,
        delay_between_retries: int = 2,
        session_timeout: int = 300,
    ) -> None:
        """
        Initialize the MarkdownConverter.

        Args:
            timeout: Timeout in seconds for individual HTTP requests.
            retries: Number of retries for failed HTTP requests.
            delay_between_retries: Delay in seconds between retries.
            session_timeout: Total session timeout in seconds for the aiohttp client.
        """
        self.timeout = timeout
        self.retries = retries
        self.delay_between_retries = delay_between_retries
        self.session_timeout = session_timeout
        self.markitdown_converter = MarkItDown()

    async def convert_urls_to_markdown(
        self, file_urls: List[str]
    ) -> Dict[str, Optional[str]]:
        """
        Convert a list of files hosted over URLs to Markdown.

        Args:
            file_urls: A list of URLs to the files to be converted.

        Returns:
            A dictionary where keys are original file URLs and values are the
            markdown content or None if conversion failed for that URL.
        """
        results: Dict[str, Optional[str]] = {}

        connector = aiohttp.TCPConnector(limit_per_host=10)
        timeout_config = aiohttp.ClientTimeout(total=self.session_timeout)

        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout_config
        ) as session:
            tasks = [self._download_and_convert(session, url) for url in file_urls]

            for result in await asyncio.gather(*tasks, return_exceptions=True):
                if isinstance(result, Exception):
                    logger.error(f"Unhandled exception during task execution: {result}")
                else:
                    url, markdown_content = result
                    results[url] = markdown_content

        return results

    async def _download_and_convert(
        self, session: aiohttp.ClientSession, url: str
    ) -> Tuple[str, Optional[str]]:
        """
        Download a single file and convert it to Markdown.

        Args:
            session: The aiohttp client session.
            url: The URL to download and convert.

        Returns:
            A tuple of (url, markdown_content_or_none).
        """
        temp_file_path: Optional[str] = None

        for attempt in range(self.retries):
            try:
                logger.info(f"Attempt {attempt + 1} of {self.retries} for URL: {url}")

                async with session.get(url, timeout=self.timeout) as response:
                    response.raise_for_status()

                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        temp_file_path = temp_file.name
                        async for chunk in response.content.iter_chunked(8192):
                            temp_file.write(chunk)
                        temp_file.flush()

                conversion_result = self.markitdown_converter.convert(temp_file_path)

                if not conversion_result or not conversion_result.markdown:
                    raise MarkdownConversionError(
                        f"MarkItDown returned empty content for {url}"
                    )

                logger.info(f"Successfully converted '{url}' to markdown")

                return url, conversion_result.markdown

            except aiohttp.ClientError as e:
                logger.warning(f"HTTP error for {url} (Attempt {attempt + 1}): {e}")
            except MarkdownConversionError as e:
                logger.warning(f"Markdown conversion error for {url} (Attempt {attempt + 1}): {e}")
            except Exception as e:
                logger.error(f"Unexpected error for {url} (Attempt {attempt + 1}): {e}")
            finally:
                if temp_file_path and os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

            if attempt < self.retries - 1:
                await asyncio.sleep(self.delay_between_retries)

        logger.error(f"Failed to convert '{url}' after {self.retries} attempts")

        return url, None


# Create a default instance for easy importing and usage
markdown_converter = MarkdownConverter()