"""
Cloudflare R2 storage service.
"""

import os
import boto3
from loguru import logger
from botocore.exceptions import ClientError
import uuid

class R2Service:
    """Service for uploading files to Cloudflare R2 storage."""

    def __init__(self):
        self.account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
        self.access_key_id = os.environ.get("CLOUDFLARE_R2_ACCESS_KEY_ID")
        self.secret_access_key = os.environ.get("CLOUDFLARE_R2_SECRET_ACCESS_KEY")
        self.bucket_name = "synapse-files"

        if not all([self.account_id, self.access_key_id, self.secret_access_key]):
            raise ValueError(
                "CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_R2_ACCESS_KEY_ID, and "
                "CLOUDFLARE_R2_SECRET_ACCESS_KEY environment variables are required"
            )

        # Configure R2 endpoint
        self.endpoint_url = f"https://{self.account_id}.r2.cloudflarestorage.com"

        # Initialize S3 client for R2
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            region_name="auto"  # R2 uses 'auto' as region
        )

    async def upload_audio_file(
        self,
        audio_content: bytes,
        notebook_id: str,
        file_extension: str = "mp3"
    ) -> str:
        """
        Upload audio file to R2 bucket.

        Args:
            audio_content: The audio file content as bytes
            notebook_id: The notebook ID to use in the filename
            file_extension: File extension (default: mp3)

        Returns:
            Public URL of the uploaded file
        """
        logger.info(f"Uploading audio file to R2 for notebook: {notebook_id}")

        # Generate file key
        random_id = str(uuid.uuid4())[:8]
        file_key = f"audios/{notebook_id}_audio_overview_{random_id}.{file_extension}"

        try:
            # Upload file to R2
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=audio_content,
                ContentType=f"audio/{file_extension}",
                ACL="public-read"  # Make file publicly accessible
            )

            # Generate public URL
            public_url = f"https://files.synapse.xyz/{file_key}"

            logger.info(f"Successfully uploaded audio file for notebook: {notebook_id}")
            logger.debug(f"Audio file URL: {public_url}")

            return public_url

        except ClientError as e:
            error_msg = f"Failed to upload audio file to R2: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error uploading to R2: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def get_public_url(self, file_key: str) -> str:
        """
        Get public URL for a file in R2.

        Args:
            file_key: The file key in the bucket

        Returns:
            Public URL of the file
        """
        return f"https://files.synapse.xyz/{file_key}"


# Singleton instance
r2_service = R2Service()