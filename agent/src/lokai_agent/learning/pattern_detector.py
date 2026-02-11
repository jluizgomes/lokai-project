"""Pattern detection for learning user behaviors."""

from typing import Any
from datetime import datetime, timedelta
from collections import defaultdict

import structlog

logger = structlog.get_logger()


class PatternDetector:
    """Detects patterns in user actions for learning."""

    def __init__(self) -> None:
        self.action_history: list[dict[str, Any]] = []
        self.sequence_counts: dict[tuple[str, ...], int] = defaultdict(int)
        self.temporal_patterns: dict[str, list[datetime]] = defaultdict(list)

    def record_action(
        self,
        action_type: str,
        context: dict[str, Any],
        timestamp: datetime | None = None,
    ) -> None:
        """Record an action for pattern detection."""
        timestamp = timestamp or datetime.now()

        self.action_history.append({
            "action": action_type,
            "context": context,
            "timestamp": timestamp,
        })

        # Keep only last 1000 actions
        if len(self.action_history) > 1000:
            self.action_history = self.action_history[-1000:]

        # Record temporal pattern
        self.temporal_patterns[action_type].append(timestamp)

        # Detect sequences
        self._update_sequences()

    def _update_sequences(self) -> None:
        """Update action sequence counts."""
        if len(self.action_history) < 2:
            return

        # Look at recent actions for sequences
        recent = self.action_history[-10:]

        # Count 2-action and 3-action sequences
        for i in range(len(recent) - 1):
            seq2 = (recent[i]["action"], recent[i + 1]["action"])
            self.sequence_counts[seq2] += 1

            if i < len(recent) - 2:
                seq3 = (recent[i]["action"], recent[i + 1]["action"], recent[i + 2]["action"])
                self.sequence_counts[seq3] += 1

    def detect_patterns(
        self,
        min_frequency: int = 3,
        min_confidence: float = 0.5,
    ) -> list[dict[str, Any]]:
        """Detect patterns from recorded actions."""
        patterns: list[dict[str, Any]] = []

        # Sequence patterns
        for sequence, count in self.sequence_counts.items():
            if count >= min_frequency:
                confidence = min(count / 10, 1.0)  # Scale confidence
                if confidence >= min_confidence:
                    patterns.append({
                        "type": "sequence",
                        "sequence": list(sequence),
                        "frequency": count,
                        "confidence": confidence,
                    })

        # Temporal patterns
        for action, timestamps in self.temporal_patterns.items():
            temporal_pattern = self._detect_temporal_pattern(timestamps)
            if temporal_pattern:
                patterns.append({
                    "type": "temporal",
                    "action": action,
                    **temporal_pattern,
                })

        logger.info("Patterns detected", count=len(patterns))
        return patterns

    def _detect_temporal_pattern(
        self,
        timestamps: list[datetime],
        min_occurrences: int = 3,
    ) -> dict[str, Any] | None:
        """Detect temporal patterns (same time of day, day of week, etc.)."""
        if len(timestamps) < min_occurrences:
            return None

        # Group by hour of day
        hour_counts: dict[int, int] = defaultdict(int)
        for ts in timestamps[-30:]:  # Look at last 30 occurrences
            hour_counts[ts.hour] += 1

        # Find most common hour
        if hour_counts:
            most_common_hour = max(hour_counts.items(), key=lambda x: x[1])
            if most_common_hour[1] >= min_occurrences:
                return {
                    "pattern": "time_of_day",
                    "hour": most_common_hour[0],
                    "frequency": most_common_hour[1],
                    "confidence": most_common_hour[1] / len(timestamps[-30:]),
                }

        return None

    def get_next_action_prediction(
        self,
        current_action: str,
        context: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Predict what action might come next."""
        predictions: list[dict[str, Any]] = []

        # Look for sequences starting with current action
        for sequence, count in self.sequence_counts.items():
            if len(sequence) >= 2 and sequence[0] == current_action:
                confidence = min(count / 5, 1.0)
                predictions.append({
                    "action": sequence[1],
                    "confidence": confidence,
                    "frequency": count,
                    "full_sequence": list(sequence),
                })

        # Sort by confidence
        predictions.sort(key=lambda x: x["confidence"], reverse=True)

        return predictions[:5]  # Return top 5 predictions

    def clear_history(self) -> None:
        """Clear action history."""
        self.action_history = []
        self.sequence_counts = defaultdict(int)
        self.temporal_patterns = defaultdict(list)
