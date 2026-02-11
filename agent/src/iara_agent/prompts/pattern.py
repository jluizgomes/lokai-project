"""Pattern detection prompts."""

PATTERN_DETECTION_PROMPT = """Analyze the following sequence of actions for patterns.

Action History:
{action_history}

Time Context:
- Current Time: {current_time}
- Day of Week: {day_of_week}
- Recent Sessions: {recent_sessions}

Look for:
1. Repeated action sequences (A -> B -> C patterns)
2. Time-based patterns (actions at specific times)
3. Context-based patterns (actions in specific directories)
4. Workflow patterns (common task sequences)

Respond in JSON format:
{{
  "patterns_detected": [
    {{
      "pattern_id": "unique_id",
      "pattern_type": "sequence|temporal|contextual|workflow",
      "description": "Human-readable description",
      "trigger": "What triggers this pattern",
      "actions": ["action1", "action2"],
      "confidence": 0.0-1.0,
      "frequency": "How often this occurs",
      "context": {{}}
    }}
  ],
  "suggestions": [
    {{
      "suggestion": "What to suggest to the user",
      "based_on_pattern": "pattern_id",
      "confidence": 0.0-1.0
    }}
  ]
}}
"""

SUGGESTION_GENERATION_PROMPT = """Based on detected patterns, generate a suggestion for the user.

Current Context:
- Directory: {current_directory}
- Time: {current_time}
- Recent Actions: {recent_actions}

Detected Pattern:
{pattern}

Generate a helpful, non-intrusive suggestion.

Respond in JSON format:
{{
  "should_suggest": true|false,
  "suggestion_type": "action|shortcut|workflow",
  "title": "Brief title",
  "description": "Explanation of the suggestion",
  "action": {{
    "tool": "tool_name if applicable",
    "parameters": {{}}
  }},
  "confidence": 0.0-1.0
}}
"""

LEARNING_FEEDBACK_PROMPT = """The user provided feedback on a suggestion.

Suggestion: {suggestion}
Feedback: {feedback} (accepted/rejected/modified)
User Modification: {modification}

How should this feedback affect the pattern learning?

Respond in JSON format:
{{
  "pattern_adjustment": {{
    "pattern_id": "id",
    "confidence_delta": -1.0 to 1.0,
    "should_disable": true|false
  }},
  "new_pattern": {{
    "should_create": true|false,
    "pattern": {{}}
  }},
  "notes": "Explanation of the adjustment"
}}
"""
