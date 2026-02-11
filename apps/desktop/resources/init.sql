-- IARA Initial Database Setup
-- This file initializes the database with default data

-- Insert default preferences
INSERT INTO preferences (key, value, category) VALUES
    ('llm.provider', '"ollama"', 'llm'),
    ('llm.model', '"llama3.2:3b"', 'llm'),
    ('llm.temperature', '0.7', 'llm'),
    ('llm.max_tokens', '2048', 'llm'),
    ('voice.enabled', 'false', 'voice'),
    ('learning.enabled', 'true', 'learning'),
    ('hotkey', '"CommandOrControl+Shift+Space"', 'app')
ON CONFLICT (key) DO NOTHING;

-- Insert default allowed commands
INSERT INTO allowed_commands (pattern, description, risk_level) VALUES
    ('^ls($|\s)', 'List directory contents', 'low'),
    ('^cat\s', 'Display file contents', 'low'),
    ('^head\s', 'Display beginning of file', 'low'),
    ('^tail\s', 'Display end of file', 'low'),
    ('^pwd$', 'Print working directory', 'low'),
    ('^echo\s', 'Print text', 'low'),
    ('^git\s+(status|log|diff|branch)', 'Git read operations', 'low'),
    ('^which\s', 'Locate command', 'low'),
    ('^date$', 'Display date', 'low'),
    ('^whoami$', 'Display current user', 'low')
ON CONFLICT (pattern) DO NOTHING;
