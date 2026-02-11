export interface QdrantConfig {
  host: string;
  port: number;
  apiKey?: string;
}

export const DEFAULT_QDRANT_CONFIG: QdrantConfig = {
  host: 'localhost',
  port: 6433,
};

export const QDRANT_COLLECTIONS = {
  // Store conversation history embeddings
  CONVERSATIONS: {
    name: 'conversations',
    vectorSize: 768, // nomic-embed-text dimension
    distance: 'Cosine' as const,
    schema: {
      sessionId: 'keyword',
      role: 'keyword',
      content: 'text',
      timestamp: 'datetime',
    },
  },

  // Store file content embeddings for context
  FILES: {
    name: 'files',
    vectorSize: 768,
    distance: 'Cosine' as const,
    schema: {
      path: 'keyword',
      filename: 'keyword',
      extension: 'keyword',
      content: 'text',
      lastModified: 'datetime',
    },
  },

  // Store code snippets for analysis
  CODE_SNIPPETS: {
    name: 'code_snippets',
    vectorSize: 768,
    distance: 'Cosine' as const,
    schema: {
      path: 'keyword',
      language: 'keyword',
      type: 'keyword', // function, class, module, etc.
      name: 'keyword',
      content: 'text',
    },
  },

  // Store learned action patterns
  PATTERNS: {
    name: 'patterns',
    vectorSize: 768,
    distance: 'Cosine' as const,
    schema: {
      patternType: 'keyword',
      trigger: 'text',
      actions: 'text',
      frequency: 'integer',
      confidence: 'float',
    },
  },
} as const;

export interface CollectionPayload {
  [key: string]: string | number | boolean | Date | null;
}

export interface SearchResult {
  id: string;
  score: number;
  payload: CollectionPayload;
}
