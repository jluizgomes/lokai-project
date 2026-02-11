"""Intent classification prompts."""

INTENT_CLASSIFICATION_PROMPT = """Analyze the user's message and classify their intent.

User message: "{message}"

Classify the intent into one of these categories:
- FILESYSTEM_READ: User wants to read or view files/directories
- FILESYSTEM_WRITE: User wants to create or modify files
- FILESYSTEM_DELETE: User wants to delete files or directories
- TERMINAL_COMMAND: User wants to execute a shell command
- GIT_OPERATION: User wants to perform git operations
- BROWSER_ACTION: User wants to interact with a browser
- CODE_ANALYSIS: User wants to understand or analyze code
- QUESTION: User is asking a question that doesn't require actions
- CLARIFICATION_NEEDED: The intent is unclear and needs clarification
- GREETING: User is greeting or making small talk
- OTHER: Doesn't fit any category

Also assess:
1. Confidence (0.0-1.0): How confident are you in this classification?
2. Risk Level (low/medium/high): What's the risk level of this action?
3. Requires Approval (true/false): Should this action require user approval?
4. Entities: Extract key entities (file paths, commands, URLs, etc.)

Respond in JSON format:
{{
  "intent": "CATEGORY",
  "confidence": 0.0-1.0,
  "risk_level": "low|medium|high",
  "requires_approval": true|false,
  "entities": {{
    "paths": [],
    "commands": [],
    "urls": [],
    "other": []
  }},
  "explanation": "Brief explanation of why this classification was chosen"
}}
"""

ENTITY_EXTRACTION_PROMPT = """Extract entities from the following user message:

Message: "{message}"

Extract:
- File paths or directory paths
- Command names or shell commands
- URLs or web addresses
- Application names
- Git branches, commits, or repository references
- Code snippets or programming language references

Respond in JSON format:
{{
  "file_paths": [],
  "directories": [],
  "commands": [],
  "urls": [],
  "applications": [],
  "git_refs": [],
  "code_references": [],
  "raw_entities": []
}}
"""
