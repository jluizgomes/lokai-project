// IARA Neo4j Knowledge Graph Schema
// This schema represents relationships between actions, contexts, and patterns

// Node types:
// - Action: Represents an action IARA can perform
// - Context: Represents a context (directory, app, time, etc.)
// - Pattern: Represents a learned pattern
// - Session: Represents a user session
// - File: Represents a file or directory
// - Tool: Represents a tool/capability

// Create constraints
CREATE CONSTRAINT action_id IF NOT EXISTS FOR (a:Action) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT context_id IF NOT EXISTS FOR (c:Context) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT pattern_id IF NOT EXISTS FOR (p:Pattern) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT session_id IF NOT EXISTS FOR (s:Session) REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT file_path IF NOT EXISTS FOR (f:File) REQUIRE f.path IS UNIQUE;
CREATE CONSTRAINT tool_name IF NOT EXISTS FOR (t:Tool) REQUIRE t.name IS UNIQUE;

// Create indexes
CREATE INDEX action_type IF NOT EXISTS FOR (a:Action) ON (a.type);
CREATE INDEX context_type IF NOT EXISTS FOR (c:Context) ON (c.type);
CREATE INDEX pattern_confidence IF NOT EXISTS FOR (p:Pattern) ON (p.confidence);
CREATE INDEX file_extension IF NOT EXISTS FOR (f:File) ON (f.extension);

// Relationship types:
// (:Action)-[:LEADS_TO {confidence: float, frequency: int}]->(:Action)
// (:Action)-[:REQUIRES]->(:Context)
// (:Action)-[:PRODUCES]->(:Context)
// (:Pattern)-[:TRIGGERS {order: int}]->(:Action)
// (:Session)-[:CONTAINS {order: int, timestamp: datetime}]->(:Action)
// (:Action)-[:USES]->(:Tool)
// (:Action)-[:AFFECTS]->(:File)
// (:File)-[:CONTAINS]->(:File)  // For directory relationships
// (:Context)-[:ACTIVE_DURING]->(:Session)
