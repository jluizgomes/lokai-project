"""Neo4j graph database client."""

from typing import Any
import structlog
from neo4j import AsyncGraphDatabase, AsyncDriver

from lokai_agent.config import settings

logger = structlog.get_logger()


class Neo4jClient:
    """Client for Neo4j graph database operations."""

    def __init__(self) -> None:
        self._driver: AsyncDriver | None = None

    async def connect(self) -> None:
        """Connect to Neo4j."""
        try:
            self._driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )
            # Verify connection
            async with self._driver.session() as session:
                await session.run("RETURN 1")
            logger.info("Connected to Neo4j")
        except Exception as e:
            logger.error("Failed to connect to Neo4j", error=str(e))
            raise

    async def disconnect(self) -> None:
        """Disconnect from Neo4j."""
        if self._driver:
            await self._driver.close()
            self._driver = None
            logger.info("Disconnected from Neo4j")

    async def record_action_sequence(
        self,
        action1_type: str,
        action2_type: str,
    ) -> None:
        """Record a sequence of actions for pattern learning."""
        if not self._driver:
            raise RuntimeError("Neo4j not connected")

        async with self._driver.session() as session:
            await session.run(
                """
                MERGE (a1:Action {type: $action1})
                MERGE (a2:Action {type: $action2})
                MERGE (a1)-[r:LEADS_TO]->(a2)
                ON CREATE SET r.confidence = 0.5, r.frequency = 1, r.createdAt = datetime()
                ON MATCH SET r.frequency = r.frequency + 1,
                             r.confidence = CASE
                               WHEN r.frequency > 10 THEN 0.9
                               WHEN r.frequency > 5 THEN 0.7
                               ELSE 0.5 + (r.frequency * 0.05)
                             END,
                             r.updatedAt = datetime()
                """,
                action1=action1_type,
                action2=action2_type,
            )

    async def find_next_actions(
        self,
        action_type: str,
        min_confidence: float = 0.5,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Find actions that commonly follow a given action."""
        if not self._driver:
            raise RuntimeError("Neo4j not connected")

        async with self._driver.session() as session:
            result = await session.run(
                """
                MATCH (a1:Action {type: $actionType})-[r:LEADS_TO]->(a2:Action)
                WHERE r.confidence > $minConfidence
                RETURN a2.type as nextAction, r.confidence as confidence, r.frequency as frequency
                ORDER BY r.confidence DESC
                LIMIT $limit
                """,
                actionType=action_type,
                minConfidence=min_confidence,
                limit=limit,
            )

            records = await result.data()
            return [
                {
                    "action": record["nextAction"],
                    "confidence": record["confidence"],
                    "frequency": record["frequency"],
                }
                for record in records
            ]

    async def create_pattern(
        self,
        pattern_id: str,
        pattern_type: str,
        trigger: str,
        confidence: float,
    ) -> None:
        """Create or update a pattern."""
        if not self._driver:
            raise RuntimeError("Neo4j not connected")

        async with self._driver.session() as session:
            await session.run(
                """
                MERGE (p:Pattern {id: $patternId})
                SET p.type = $patternType,
                    p.trigger = $trigger,
                    p.confidence = $confidence,
                    p.frequency = COALESCE(p.frequency, 0) + 1,
                    p.updatedAt = datetime()
                """,
                patternId=pattern_id,
                patternType=pattern_type,
                trigger=trigger,
                confidence=confidence,
            )

    async def link_pattern_to_action(
        self,
        pattern_id: str,
        action_type: str,
        order: int,
    ) -> None:
        """Link a pattern to an action."""
        if not self._driver:
            raise RuntimeError("Neo4j not connected")

        async with self._driver.session() as session:
            await session.run(
                """
                MATCH (p:Pattern {id: $patternId})
                MERGE (a:Action {type: $actionType})
                MERGE (p)-[r:TRIGGERS]->(a)
                SET r.order = $order
                """,
                patternId=pattern_id,
                actionType=action_type,
                order=order,
            )
