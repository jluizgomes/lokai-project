"""Action planning prompts."""

ACTION_PLANNING_PROMPT = """Based on the user's intent, create an action plan.

User Message: "{message}"
Intent: {intent}
Entities: {entities}
Current Context:
- Working Directory: {current_directory}
- Recent Files: {recent_files}

Create a step-by-step plan to fulfill the user's request. For each step:
1. Specify the tool to use
2. Specify the parameters
3. Explain what this step accomplishes
4. Note any dependencies on previous steps

Respond in JSON format:
{{
  "plan_summary": "Brief description of what will be done",
  "steps": [
    {{
      "step_number": 1,
      "tool": "tool_name",
      "parameters": {{}},
      "description": "What this step does",
      "depends_on": [],
      "risk_level": "low|medium|high",
      "requires_approval": true|false
    }}
  ],
  "total_risk_level": "low|medium|high",
  "requires_user_confirmation": true|false,
  "confirmation_message": "Message to show user if confirmation needed"
}}
"""

ROLLBACK_PLAN_PROMPT = """Create a rollback plan for the following action:

Action: {action}
Parameters: {parameters}

If this action fails or needs to be undone, what steps should be taken?

Respond in JSON format:
{{
  "can_rollback": true|false,
  "rollback_steps": [
    {{
      "step_number": 1,
      "tool": "tool_name",
      "parameters": {{}},
      "description": "What this rollback step does"
    }}
  ],
  "notes": "Any important notes about the rollback"
}}
"""

CONTEXT_GATHERING_PROMPT = """Gather context for the user's request.

User Message: "{message}"
Intent: {intent}

What additional context would be helpful to fulfill this request?
Consider:
- Current directory contents
- Related files
- Git status
- Environment variables
- Recent actions

Respond in JSON format:
{{
  "needed_context": [
    {{
      "type": "directory_listing|file_content|git_status|env_var|other",
      "target": "path or name",
      "reason": "Why this context is needed"
    }}
  ],
  "priority": "high|medium|low"
}}
"""
