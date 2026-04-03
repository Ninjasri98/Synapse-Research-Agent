from typing import List, Optional
from loguru import logger
from openai import AsyncOpenAI
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as rest
from qdrant_client.http.models import Distance, VectorParams
class QdrantSourceStore:
    """Service for storing and retrieving source documents using Qdrant and OpenAI embeddings."""

    def __init__(
        self,
        qdrant_url: str = "localhost",
        qdrant_api_key: Optional[str] = None,
        collection_name: str = "sources",
        embedding_model: str = "text-embedding-3-small",
        openai_api_key: Optional[str] = None,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
    ):
        """Initialize Qdrant source store.

        Args:
            qdrant_url: URL of Qdrant server
            qdrant_api_key: API key for Qdrant
            collection_name: Name of the collection to store sources
            embedding_model: OpenAI embedding model name
            openai_api_key: OpenAI API key
            chunk_size: Size of chunks for text splitting
            chunk_overlap: Overlap between chunks
        """
        logger.info(f"Initializing QdrantSourceStore with collection: {collection_name}")

        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self._initialized = False

        # Initialize Qdrant client
        logger.info(f"Connecting to Qdrant at {qdrant_url}")
        self.qdrant_client = AsyncQdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key,
            prefer_grpc=True,
        )

        # Initialize OpenAI client
        logger.info("Initializing OpenAI client")
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)

    async def initialize(self) -> None:
        """Initialize the Qdrant collection asynchronously."""
        if not self._initialized:
            await self._create_collection_if_not_exists()
            self._initialized = True

    async def _create_collection_if_not_exists(self) -> None:
        """Create collection if it doesn't exist."""
        logger.info("Checking if collection exists")
        collections_response = await self.qdrant_client.get_collections()
        collections = collections_response.collections

        collection_names = [collection.name for collection in collections]

        if self.collection_name not in collection_names:
            logger.info(f"Collection {self.collection_name} does not exist, creating...")
            # Get vector size from embedding model
            vector_size = await self._get_embedding_size()

            # Create collection
            await self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE,
                ),
            )

            # Create payload index for notebook_id for faster filtering
            logger.info("Creating payload index for notebook_id")
            await self.qdrant_client.create_payload_index(
                collection_name=self.collection_name,
                field_name="notebook_id",
                field_schema=rest.PayloadSchemaType.KEYWORD,
            )

            logger.info(f"Created collection: {self.collection_name}")

    async def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI."""
        if not self._initialized:
            await self.initialize()
        logger.info(f"Getting embedding using model {self.embedding_model}")
        response = await self.openai_client.embeddings.create(
            input=text,
            model=self.embedding_model,
        )
        return response.data[0].embedding

    async def _get_embedding_size(self) -> int:
        """Get embedding size for the model."""
        # Simple text to get embedding size
        test_text = "Test"
        embedding = await self.openai_client.embeddings.create(
            input=test_text,
            model=self.embedding_model,
        )
        return len(embedding.data[0].embedding)


    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks based on chunk size and overlap.

        Args:
            text: The text to split into chunks

        Returns:
            List of text chunks with specified size and overlap
        """
        if not text:
            logger.warning("Empty text provided for chunking")
            return []

        logger.info(f"Chunking text with size {self.chunk_size} and overlap {self.chunk_overlap}")
        # Use list comprehension for cleaner chunk creation
        tokens = text.split()
        chunk_starts = range(0, len(tokens), self.chunk_size - self.chunk_overlap)
        chunks = [
            " ".join(tokens[i:i + self.chunk_size])
            for i in chunk_starts
            if i + self.chunk_size <= len(tokens)
        ]

        # Handle remaining tokens if any
        if tokens[chunk_starts[-1]:]:
            chunks.append(" ".join(tokens[chunk_starts[-1]:]))

        logger.info(f"Created {len(chunks)} chunks")
        return chunks
