export interface Neo4jConfig {
  uri: string;
  user: string;
  password: string;
  database?: string;
}

export const DEFAULT_NEO4J_CONFIG: Neo4jConfig = {
  uri: 'bolt://localhost:7688',
  user: 'neo4j',
  password: 'lokai_password',
  database: 'neo4j',
};

export const NEO4J_SCHEMA = `
// Lokai Neo4j Knowledge Graph Schema
// This schema represents relationships between actions, contexts, and patterns

// Node types:
// - Action: Represents an action Lokai can perform
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
// Action -[:LEADS_TO]-> Action (with confidence weight)
// Action -[:REQUIRES]-> Context
// Action -[:PRODUCES]-> Context
// Pattern -[:TRIGGERS]-> Action
// Session -[:CONTAINS]-> Action
// Action -[:USES]-> Tool
// Action -[:AFFECTS]-> File
`;

export const NEO4J_CYPHER_QUERIES = {
  // Find actions that commonly follow a given action
  FIND_NEXT_ACTIONS: `
    MATCH (a1:Action {type: $actionType})-[r:LEADS_TO]->(a2:Action)
    WHERE r.confidence > $minConfidence
    RETURN a2.type as nextAction, r.confidence as confidence, r.frequency as frequency
    ORDER BY r.confidence DESC
    LIMIT $limit
  `,

  // Find patterns for a given context
  FIND_PATTERNS_FOR_CONTEXT: `
    MATCH (p:Pattern)-[:REQUIRES]->(c:Context {type: $contextType})
    WHERE p.confidence > $minConfidence AND p.isActive = true
    RETURN p
    ORDER BY p.confidence DESC
    LIMIT $limit
  `,

  // Record an action sequence
  RECORD_ACTION_SEQUENCE: `
    MERGE (a1:Action {type: $action1Type})
    MERGE (a2:Action {type: $action2Type})
    MERGE (a1)-[r:LEADS_TO]->(a2)
    ON CREATE SET r.confidence = 0.5, r.frequency = 1, r.createdAt = datetime()
    ON MATCH SET r.frequency = r.frequency + 1,
                 r.confidence = CASE
                   WHEN r.frequency > 10 THEN 0.9
                   WHEN r.frequency > 5 THEN 0.7
                   ELSE 0.5 + (r.frequency * 0.05)
                 END,
                 r.updatedAt = datetime()
    RETURN r
  `,

  // Create or update a pattern
  UPSERT_PATTERN: `
    MERGE (p:Pattern {id: $patternId})
    SET p.type = $patternType,
        p.trigger = $trigger,
        p.confidence = $confidence,
        p.frequency = COALESCE(p.frequency, 0) + 1,
        p.updatedAt = datetime()
    RETURN p
  `,

  // Link pattern to action
  LINK_PATTERN_ACTION: `
    MATCH (p:Pattern {id: $patternId})
    MERGE (a:Action {type: $actionType})
    MERGE (p)-[r:TRIGGERS]->(a)
    SET r.order = $order
    RETURN p, a
  `,
} as const;
