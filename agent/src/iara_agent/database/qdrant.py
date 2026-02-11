"""Qdrant vector database client."""

from typing import Any
import structlog
from qdrant_client import QdrantClient as QdrantSDK
from qdrant_client.models import Distance, VectorParams, PointStruct

from iara_agent.config import settings

logger = structlog.get_logger()


class QdrantClient:
    """Client for Qdrant vector database operations."""

    VECTOR_SIZE = 768  # nomic-embed-text dimension

    def __init__(self) -> None:
        self._client: QdrantSDK | None = None

    async def connect(self) -> None:
        """Connect to Qdrant."""
        try:
            self._client = QdrantSDK(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
            )
            # Initialize collections if they don't exist
            await self._init_collections()
            logger.info("Connected to Qdrant")
        except Exception as e:
            logger.error("Failed to connect to Qdrant", error=str(e))
            raise

    async def _init_collections(self) -> None:
        """Initialize required collections."""
        if not self._client:
            return

        collections = ["conversations", "files", "patterns"]

        for collection_name in collections:
            try:
                self._client.get_collection(collection_name)
            except Exception:
                self._client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=self.VECTOR_SIZE,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(f"Created collection: {collection_name}")

    async def store_embedding(
        self,
        collection: str,
        id: str,
        vector: list[float],
        payload: dict[str, Any],
    ) -> None:
        """Store an embedding with its payload."""
        if not self._client:
            raise RuntimeError("Qdrant not connected")

        self._client.upsert(
            collection_name=collection,
            points=[
                PointStruct(
                    id=hash(id) % (2**63),  # Convert string ID to int
                    vector=vector,
                    payload={"id": id, **payload},
                )
            ],
        )

    async def search(
        self,
        collection: str,
        vector: list[float],
        limit: int = 5,
        score_threshold: float = 0.5,
    ) -> list[dict[str, Any]]:
        """Search for similar vectors."""
        if not self._client:
            raise RuntimeError("Qdrant not connected")

        results = self._client.search(
            collection_name=collection,
            query_vector=vector,
            limit=limit,
            score_threshold=score_threshold,
        )

        return [
            {
                "id": result.payload.get("id"),
                "score": result.score,
                "payload": result.payload,
            }
            for result in results
        ]

    async def delete(self, collection: str, ids: list[str]) -> None:
        """Delete points by ID."""
        if not self._client:
            raise RuntimeError("Qdrant not connected")

        int_ids = [hash(id) % (2**63) for id in ids]
        self._client.delete(
            collection_name=collection,
            points_selector=int_ids,
        )

    async def disconnect(self) -> None:
        """Disconnect from Qdrant."""
        self._client = None
        logger.info("Disconnected from Qdrant")
