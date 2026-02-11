export interface IpcRequest<T = unknown> {
  id: string;
  channel: string;
  data: T;
  timestamp: number;
}

export interface IpcResponse<T = unknown> {
  id: string;
  success: boolean;
  data?: T;
  error?: string;
  timestamp: number;
}

export interface StreamingToken {
  id: string;
  token: string;
  index: number;
}

export interface StreamingComplete {
  id: string;
  content: string;
  totalTokens: number;
}

export interface AgentStatusResponse {
  running: boolean;
  provider?: string;
  model?: string;
  lastError?: string;
}
