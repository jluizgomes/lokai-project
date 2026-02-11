import { useEffect, useCallback } from 'react';

export function useIpc() {
  const sendMessage = useCallback(async (message: string) => {
    return window.iara.agent.sendMessage(message);
  }, []);

  const sendMessageStreaming = useCallback(async (message: string) => {
    return window.iara.agent.sendMessageStreaming(message);
  }, []);

  const getAgentStatus = useCallback(async () => {
    return window.iara.agent.getStatus();
  }, []);

  const executeTool = useCallback(async (toolName: string, params: unknown) => {
    return window.iara.agent.executeTool(toolName, params);
  }, []);

  const cancelOperation = useCallback(async () => {
    return window.iara.agent.cancel();
  }, []);

  return {
    sendMessage,
    sendMessageStreaming,
    getAgentStatus,
    executeTool,
    cancelOperation,
  };
}

export function useStreamingTokens(onToken: (token: string) => void) {
  useEffect(() => {
    const unsubscribe = window.iara.agent.onStreamToken(onToken);
    return () => { unsubscribe(); };
  }, [onToken]);
}

export function useStreamingComplete(onComplete: (response: string) => void) {
  useEffect(() => {
    const unsubscribe = window.iara.agent.onStreamComplete(onComplete);
    return () => { unsubscribe(); };
  }, [onComplete]);
}

export function useStreamingError(onError: (error: string) => void) {
  useEffect(() => {
    const unsubscribe = window.iara.agent.onStreamError(onError);
    return () => { unsubscribe(); };
  }, [onError]);
}
