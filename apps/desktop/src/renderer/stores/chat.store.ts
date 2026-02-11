import { create } from 'zustand';

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  status?: 'sending' | 'streaming' | 'complete' | 'error';
  toolCalls?: {
    name: string;
    status: 'pending' | 'running' | 'complete' | 'error';
    result?: string;
  }[];
}

export interface ApprovalRequest {
  id: string;
  action: string;
  description: string;
  riskLevel: 'low' | 'medium' | 'high';
  preview?: string;
  metadata?: Record<string, unknown>;
}

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  isStreaming: boolean;
  currentStreamingMessage: string;
  approvalRequest: ApprovalRequest | null;
  error: string | null;

  // Actions
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  updateMessage: (id: string, updates: Partial<Message>) => void;
  appendToStreamingMessage: (token: string) => void;
  completeStreamingMessage: (content: string) => void;
  setIsLoading: (isLoading: boolean) => void;
  setIsStreaming: (isStreaming: boolean) => void;
  setApprovalRequest: (request: ApprovalRequest | null) => void;
  setError: (error: string | null) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isLoading: false,
  isStreaming: false,
  currentStreamingMessage: '',
  approvalRequest: null,
  error: null,

  addMessage: (message) => {
    const newMessage: Message = {
      ...message,
      id: crypto.randomUUID(),
      timestamp: new Date(),
    };
    set((state) => ({
      messages: [...state.messages, newMessage],
    }));
  },

  updateMessage: (id, updates) => {
    set((state) => ({
      messages: state.messages.map((msg) =>
        msg.id === id ? { ...msg, ...updates } : msg
      ),
    }));
  },

  appendToStreamingMessage: (token) => {
    set((state) => ({
      currentStreamingMessage: state.currentStreamingMessage + token,
    }));
  },

  completeStreamingMessage: (content) => {
    const { messages } = get();
    const lastMessage = messages[messages.length - 1];

    if (lastMessage && lastMessage.role === 'assistant' && lastMessage.status === 'streaming') {
      set((state) => ({
        messages: state.messages.map((msg) =>
          msg.id === lastMessage.id
            ? { ...msg, content, status: 'complete' as const }
            : msg
        ),
        currentStreamingMessage: '',
        isStreaming: false,
      }));
    } else {
      set({
        currentStreamingMessage: '',
        isStreaming: false,
      });
    }
  },

  setIsLoading: (isLoading) => set({ isLoading }),

  setIsStreaming: (isStreaming) => set({ isStreaming }),

  setApprovalRequest: (request) => set({ approvalRequest: request }),

  setError: (error) => set({ error }),

  clearMessages: () => set({ messages: [], currentStreamingMessage: '' }),
}));
