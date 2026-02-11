"""Suggestion engine for proactive assistance."""

from typing import Any
from datetime import datetime

import structlog

from lokai_agent.learning.pattern_detector import PatternDetector
from lokai_agent.learning.knowledge_graph import KnowledgeGraphUpdater

logger = structlog.get_logger()


class SuggestionEngine:
    """Generates proactive suggestions based on learned patterns."""

    def __init__(
        self,
        pattern_detector: PatternDetector,
        knowledge_graph: KnowledgeGraphUpdater | None = None,
    ) -> None:
        self.pattern_detector = pattern_detector
        self.knowledge_graph = knowledge_graph
        self.suggestion_history: list[dict[str, Any]] = []
        self.feedback_stats: dict[str, dict[str, int]] = {}

    async def generate_suggestions(
        self,
        current_action: str | None = None,
        context: dict[str, Any] | None = None,
        max_suggestions: int = 3,
    ) -> list[dict[str, Any]]:
        """Generate suggestions based on current context."""
        suggestions: list[dict[str, Any]] = []

        # Get predictions from pattern detector
        if current_action:
            predictions = self.pattern_detector.get_next_action_prediction(
                current_action,
                context,
            )

            for pred in predictions[:max_suggestions]:
                if pred["confidence"] >= 0.5:
                    suggestions.append({
                        "id": f"pred_{hash(pred['action'])}",
                        "type": "action",
                        "title": f"Next: {pred['action']}",
                        "description": f"Based on your pattern of {current_action} -> {pred['action']}",
                        "action": pred["action"],
                        "confidence": pred["confidence"],
                        "source": "pattern_detector",
                    })

        # Get suggestions from knowledge graph
        if self.knowledge_graph and current_action:
            try:
                kg_suggestions = await self.knowledge_graph.get_suggested_next_actions(
                    current_action,
                    limit=max_suggestions,
                )

                for sugg in kg_suggestions:
                    suggestions.append({
                        "id": f"kg_{hash(sugg['action'])}",
                        "type": "action",
                        "title": f"Suggested: {sugg['action']}",
                        "description": f"Based on historical patterns (confidence: {sugg['confidence']:.0%})",
                        "action": sugg["action"],
                        "confidence": sugg["confidence"],
                        "source": "knowledge_graph",
                    })
            except Exception as e:
                logger.warning("Failed to get knowledge graph suggestions", error=str(e))

        # Deduplicate and sort by confidence
        seen_actions = set()
        unique_suggestions = []
        for sugg in sorted(suggestions, key=lambda x: x["confidence"], reverse=True):
            if sugg["action"] not in seen_actions:
                seen_actions.add(sugg["action"])
                unique_suggestions.append(sugg)

        # Record suggestion history
        for sugg in unique_suggestions[:max_suggestions]:
            self.suggestion_history.append({
                **sugg,
                "shown_at": datetime.now(),
                "context": context,
            })

        logger.info("Suggestions generated", count=len(unique_suggestions[:max_suggestions]))

        return unique_suggestions[:max_suggestions]

    async def record_feedback(
        self,
        suggestion_id: str,
        feedback: str,  # "accepted", "rejected", "modified"
        modification: str | None = None,
    ) -> None:
        """Record user feedback on a suggestion."""
        # Initialize stats for this suggestion if needed
        if suggestion_id not in self.feedback_stats:
            self.feedback_stats[suggestion_id] = {
                "accepted": 0,
                "rejected": 0,
                "modified": 0,
            }

        # Update stats
        self.feedback_stats[suggestion_id][feedback] += 1

        # Find the suggestion in history
        suggestion = None
        for sugg in reversed(self.suggestion_history):
            if sugg["id"] == suggestion_id:
                suggestion = sugg
                break

        if suggestion:
            # Update knowledge graph confidence if available
            if self.knowledge_graph:
                delta = 0.1 if feedback == "accepted" else -0.05
                try:
                    await self.knowledge_graph.update_pattern_confidence(
                        suggestion_id,
                        delta,
                    )
                except Exception as e:
                    logger.warning("Failed to update pattern confidence", error=str(e))

        logger.info(
            "Suggestion feedback recorded",
            suggestion_id=suggestion_id,
            feedback=feedback,
        )

    def get_suggestion_stats(self) -> dict[str, Any]:
        """Get statistics about suggestion performance."""
        total_shown = len(self.suggestion_history)
        total_accepted = sum(
            stats["accepted"]
            for stats in self.feedback_stats.values()
        )
        total_rejected = sum(
            stats["rejected"]
            for stats in self.feedback_stats.values()
        )

        acceptance_rate = (
            total_accepted / (total_accepted + total_rejected)
            if (total_accepted + total_rejected) > 0
            else 0
        )

        return {
            "total_shown": total_shown,
            "total_accepted": total_accepted,
            "total_rejected": total_rejected,
            "acceptance_rate": acceptance_rate,
            "unique_suggestions": len(self.feedback_stats),
        }
