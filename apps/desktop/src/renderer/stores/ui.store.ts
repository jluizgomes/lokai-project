import { create } from 'zustand';

interface UIState {
  showSettings: boolean;
  activeSettingsTab: 'general' | 'permissions' | 'learning' | 'voice' | 'about';
  sidebarOpen: boolean;
  theme: 'light' | 'dark' | 'system';
  agentStatus: 'connected' | 'disconnected' | 'processing';

  // Actions
  setShowSettings: (show: boolean) => void;
  setActiveSettingsTab: (tab: UIState['activeSettingsTab']) => void;
  setSidebarOpen: (open: boolean) => void;
  setTheme: (theme: UIState['theme']) => void;
  setAgentStatus: (status: UIState['agentStatus']) => void;
}

export const useUIStore = create<UIState>((set) => ({
  showSettings: false,
  activeSettingsTab: 'general',
  sidebarOpen: false,
  theme: 'dark',
  agentStatus: 'disconnected',

  setShowSettings: (show) => set({ showSettings: show }),
  setActiveSettingsTab: (tab) => set({ activeSettingsTab: tab }),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setTheme: (theme) => set({ theme }),
  setAgentStatus: (status) => set({ agentStatus: status }),
}));
