"""Knowledge graph updater for learning relationships."""

from typing import Any

import structlog

from lokai_agent.database.neo4j import Neo4jClient

logger = structlog.get_logger()


class KnowledgeGraphUpdater:
    """Updates the knowledge graph with learned patterns."""

    def __init__(self, neo4j_client: Neo4jClient) -> None:
        self.neo4j = neo4j_client

    async def record_action_sequence(
        self,
        actions: list[str],
    ) -> None:
        """Record a sequence of actions to the knowledge graph."""
        if len(actions) < 2:
            return

        for i in range(len(actions) - 1):
            await self.neo4j.record_action_sequence(
                actions[i],
                actions[i + 1],
            )

        logger.info("Action sequence recorded", length=len(actions))

    async def record_pattern(
        self,
        pattern_id: str,
        pattern_type: str,
        trigger: str,
        actions: list[str],
        confidence: float,
    ) -> None:
        """Record a detected pattern to the knowledge graph."""
        await self.neo4j.create_pattern(
            pattern_id=pattern_id,
            pattern_type=pattern_type,
            trigger=trigger,
            confidence=confidence,
        )

        # Link pattern to actions
        for i, action in enumerate(actions):
            await self.neo4j.link_pattern_to_action(
                pattern_id=pattern_id,
                action_type=action,
                order=i,
            )

        logger.info(
            "Pattern recorded to knowledge graph",
            pattern_id=pattern_id,
            actions_count=len(actions),
        )

    async def get_suggested_next_actions(
        self,
        current_action: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Get suggested next actions from the knowledge graph."""
        suggestions = await self.neo4j.find_next_actions(
            action_type=current_action,
            min_confidence=0.3,
            limit=limit,
        )

        return suggestions

    async def update_pattern_confidence(
        self,
        pattern_id: str,
        delta: float,
    ) -> None:
        """Update the confidence of a pattern based on feedback."""
        # This would update the pattern confidence in Neo4j
        # Implementation depends on the specific feedback mechanism
        pass
