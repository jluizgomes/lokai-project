import { create } from 'zustand';

interface Permission {
  id: string;
  category: 'filesystem' | 'terminal' | 'browser' | 'app' | 'clipboard';
  action: string;
  allowed: boolean;
  requiresApproval: boolean;
  paths?: string[];
  commands?: string[];
}

interface LLMSettings {
  provider: 'ollama' | 'llama.cpp' | 'openai';
  model: string;
  temperature: number;
  maxTokens: number;
  ollamaHost: string;
}

interface VoiceSettings {
  enabled: boolean;
  wakeWord: string;
  sttEngine: 'whisper' | 'vosk';
  ttsEngine: 'piper' | 'espeak';
  language: string;
  autoListen: boolean;
}

interface SettingsState {
  permissions: Permission[];
  llm: LLMSettings;
  voice: VoiceSettings;
  hotkey: string;
  startOnBoot: boolean;
  showInDock: boolean;
  allowedDirectories: string[];
  blockedDirectories: string[];

  // Actions
  updatePermission: (id: string, updates: Partial<Permission>) => void;
  addAllowedDirectory: (path: string) => void;
  removeAllowedDirectory: (path: string) => void;
  updateLLMSettings: (settings: Partial<LLMSettings>) => void;
  updateVoiceSettings: (settings: Partial<VoiceSettings>) => void;
  setHotkey: (hotkey: string) => void;
  setStartOnBoot: (start: boolean) => void;
  setShowInDock: (show: boolean) => void;
}

const defaultPermissions: Permission[] = [
  {
    id: 'fs-read',
    category: 'filesystem',
    action: 'read',
    allowed: true,
    requiresApproval: false,
  },
  {
    id: 'fs-write',
    category: 'filesystem',
    action: 'write',
    allowed: true,
    requiresApproval: true,
  },
  {
    id: 'fs-delete',
    category: 'filesystem',
    action: 'delete',
    allowed: true,
    requiresApproval: true,
  },
  {
    id: 'terminal-read',
    category: 'terminal',
    action: 'read',
    allowed: true,
    requiresApproval: false,
  },
  {
    id: 'terminal-execute',
    category: 'terminal',
    action: 'execute',
    allowed: true,
    requiresApproval: true,
  },
  {
    id: 'browser-navigate',
    category: 'browser',
    action: 'navigate',
    allowed: true,
    requiresApproval: false,
  },
  {
    id: 'browser-action',
    category: 'browser',
    action: 'action',
    allowed: true,
    requiresApproval: true,
  },
  {
    id: 'app-control',
    category: 'app',
    action: 'control',
    allowed: true,
    requiresApproval: true,
  },
  {
    id: 'clipboard-read',
    category: 'clipboard',
    action: 'read',
    allowed: true,
    requiresApproval: false,
  },
  {
    id: 'clipboard-write',
    category: 'clipboard',
    action: 'write',
    allowed: true,
    requiresApproval: true,
  },
];

export const useSettingsStore = create<SettingsState>((set) => ({
  permissions: defaultPermissions,
  llm: {
    provider: 'ollama',
    model: 'llama3.2:3b',
    temperature: 0.7,
    maxTokens: 2048,
    ollamaHost: 'http://localhost:11439',
  },
  voice: {
    enabled: false,
    wakeWord: 'hey lokai',
    sttEngine: 'whisper',
    ttsEngine: 'piper',
    language: 'en',
    autoListen: false,
  },
  hotkey: 'CommandOrControl+Shift+Space',
  startOnBoot: false,
  showInDock: true,
  allowedDirectories: [],
  blockedDirectories: [],

  updatePermission: (id, updates) =>
    set((state) => ({
      permissions: state.permissions.map((p) =>
        p.id === id ? { ...p, ...updates } : p
      ),
    })),

  addAllowedDirectory: (path) =>
    set((state) => ({
      allowedDirectories: [...state.allowedDirectories, path],
    })),

  removeAllowedDirectory: (path) =>
    set((state) => ({
      allowedDirectories: state.allowedDirectories.filter((p) => p !== path),
    })),

  updateLLMSettings: (settings) =>
    set((state) => ({
      llm: { ...state.llm, ...settings },
    })),

  updateVoiceSettings: (settings) =>
    set((state) => ({
      voice: { ...state.voice, ...settings },
    })),

  setHotkey: (hotkey) => set({ hotkey }),

  setStartOnBoot: (start) => set({ startOnBoot: start }),

  setShowInDock: (show) => set({ showInDock: show }),
}));
