export interface AgentState {
  sessionId: string;
  messages: AgentMessage[];
  currentIntent: string | null;
  context: AgentContext;
  pendingActions: PendingAction[];
  learningEnabled: boolean;
}

export interface AgentMessage {
  id: string;
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
  toolCalls?: ToolCall[];
  timestamp: Date;
}

export interface AgentContext {
  currentDirectory?: string;
  activeApp?: string;
  clipboard?: string;
  recentFiles?: string[];
  environmentVariables?: Record<string, string>;
  systemInfo?: SystemInfo;
}

export interface SystemInfo {
  platform: string;
  hostname: string;
  homeDir: string;
  username: string;
}

export interface ToolCall {
  id: string;
  name: string;
  parameters: Record<string, unknown>;
  status: 'pending' | 'running' | 'complete' | 'error';
  result?: string;
  error?: string;
  startedAt?: Date;
  completedAt?: Date;
}

export interface PendingAction {
  id: string;
  type: string;
  description: string;
  requiresApproval: boolean;
  riskLevel: 'low' | 'medium' | 'high';
  parameters: Record<string, unknown>;
}

export interface LearningPattern {
  id: string;
  pattern: string;
  frequency: number;
  lastSeen: Date;
  confidence: number;
  actions: string[];
}

export interface AgentSuggestion {
  id: string;
  type: 'action' | 'shortcut' | 'workflow';
  title: string;
  description: string;
  confidence: number;
  basedOn: string[];
}
