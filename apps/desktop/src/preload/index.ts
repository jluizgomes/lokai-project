import { contextBridge, ipcRenderer } from 'electron';

// Expose protected methods that allow the renderer process to use
// ipcRenderer without exposing the entire object
const api = {
  // Agent communication
  agent: {
    sendMessage: (message: string) => ipcRenderer.invoke('agent:send-message', message),
    sendMessageStreaming: (message: string) =>
      ipcRenderer.invoke('agent:send-message-streaming', message),
    getStatus: () => ipcRenderer.invoke('agent:status'),
    executeTool: (toolName: string, params: unknown) =>
      ipcRenderer.invoke('agent:execute-tool', toolName, params),
    cancel: () => ipcRenderer.invoke('agent:cancel'),
    onStreamToken: (callback: (token: string) => void) => {
      const listener = (_event: Electron.IpcRendererEvent, token: string) => callback(token);
      ipcRenderer.on('agent:stream-token', listener);
      return () => ipcRenderer.removeListener('agent:stream-token', listener);
    },
    onStreamComplete: (callback: (response: string) => void) => {
      const listener = (_event: Electron.IpcRendererEvent, response: string) => callback(response);
      ipcRenderer.on('agent:stream-complete', listener);
      return () => ipcRenderer.removeListener('agent:stream-complete', listener);
    },
    onStreamError: (callback: (error: string) => void) => {
      const listener = (_event: Electron.IpcRendererEvent, error: string) => callback(error);
      ipcRenderer.on('agent:stream-error', listener);
      return () => ipcRenderer.removeListener('agent:stream-error', listener);
    },
  },

  // Approval system
  approval: {
    respond: (id: string, response: { approved: boolean; remember?: boolean }) =>
      ipcRenderer.invoke('approval:respond', id, response),
    list: () => ipcRenderer.invoke('approval:list'),
    cancel: (id: string) => ipcRenderer.invoke('approval:cancel', id),
    onShowApproval: (
      callback: (request: {
        id: string;
        action: string;
        description: string;
        riskLevel: 'low' | 'medium' | 'high';
        preview?: string;
      }) => void
    ) => {
      const listener = (_event: Electron.IpcRendererEvent, request: Parameters<typeof callback>[0]) =>
        callback(request);
      ipcRenderer.on('approval:show', listener);
      return () => ipcRenderer.removeListener('approval:show', listener);
    },
  },

  // System utilities
  system: {
    getInfo: () => ipcRenderer.invoke('system:info'),
    openExternal: (url: string) => ipcRenderer.invoke('system:open-external', url),
    openPath: (path: string) => ipcRenderer.invoke('system:open-path', path),
    showInFolder: (path: string) => ipcRenderer.invoke('system:show-in-folder', path),
    getPath: (name: string) => ipcRenderer.invoke('system:get-path', name),
  },

  // Window controls
  window: {
    minimize: () => ipcRenderer.invoke('window:minimize'),
    maximize: () => ipcRenderer.invoke('window:maximize'),
    close: () => ipcRenderer.invoke('window:close'),
    isMaximized: () => ipcRenderer.invoke('window:is-maximized'),
  },

  // Event listeners
  on: {
    focusInput: (callback: () => void) => {
      const listener = () => callback();
      ipcRenderer.on('focus-input', listener);
      return () => ipcRenderer.removeListener('focus-input', listener);
    },
    openSettings: (callback: () => void) => {
      const listener = () => callback();
      ipcRenderer.on('open-settings', listener);
      return () => ipcRenderer.removeListener('open-settings', listener);
    },
    quickAction: (callback: () => void) => {
      const listener = () => callback();
      ipcRenderer.on('quick-action', listener);
      return () => ipcRenderer.removeListener('quick-action', listener);
    },
  },
};

// Expose API to renderer
contextBridge.exposeInMainWorld('lokai', api);

// Type declarations for the exposed API
declare global {
  interface Window {
    lokai: typeof api;
  }
}
