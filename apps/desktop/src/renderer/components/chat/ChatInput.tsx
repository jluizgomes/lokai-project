import { useState, useRef, useEffect, KeyboardEvent } from 'react';
import { Send, Mic, StopCircle } from 'lucide-react';
import { useChatStore } from '../../stores/chat.store';
import { useUIStore } from '../../stores/ui.store';
import { cn } from '../../lib/utils';

export function ChatInput() {
  const [input, setInput] = useState('');
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const {
    addMessage,
    setIsLoading,
    setIsStreaming,
    appendToStreamingMessage,
    completeStreamingMessage,
    setError,
    isLoading,
    isStreaming,
  } = useChatStore();
  const { setAgentStatus } = useUIStore();

  useEffect(() => {
    // Listen for focus-input event
    const unsubscribe = window.iara.on.focusInput(() => {
      inputRef.current?.focus();
    });

    // Focus input on mount
    inputRef.current?.focus();

    return () => {
      unsubscribe();
    };
  }, []);

  const handleSubmit = async () => {
    const trimmedInput = input.trim();
    if (!trimmedInput || isLoading || isStreaming) return;

    setInput('');

    // Add user message
    addMessage({
      role: 'user',
      content: trimmedInput,
      status: 'complete',
    });

    setIsLoading(true);
    setAgentStatus('processing');

    try {
      // Add placeholder for assistant message
      addMessage({
        role: 'assistant',
        content: '',
        status: 'streaming',
      });

      setIsStreaming(true);
      setIsLoading(false);

      // Setup streaming listeners
      const unsubscribeToken = window.iara.agent.onStreamToken((token) => {
        appendToStreamingMessage(token);
      });

      const unsubscribeComplete = window.iara.agent.onStreamComplete((response) => {
        completeStreamingMessage(response);
        setAgentStatus('connected');
        unsubscribeToken();
        unsubscribeComplete();
      });

      const unsubscribeError = window.iara.agent.onStreamError((error) => {
        setError(error);
        setIsStreaming(false);
        setAgentStatus('connected');
        unsubscribeToken();
        unsubscribeComplete();
        unsubscribeError();
      });

      // Send message with streaming
      await window.iara.agent.sendMessageStreaming(trimmedInput);
    } catch (error) {
      setError((error as Error).message);
      setIsLoading(false);
      setIsStreaming(false);
      setAgentStatus('connected');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleCancel = async () => {
    try {
      await window.iara.agent.cancel();
      setIsLoading(false);
      setIsStreaming(false);
      setAgentStatus('connected');
    } catch (error) {
      console.error('Failed to cancel:', error);
    }
  };

  return (
    <div className="border-t border-border p-3 bg-card">
      <div className="flex items-end gap-2">
        <div className="flex-1 relative">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask IARA anything..."
            disabled={isLoading || isStreaming}
            rows={1}
            className={cn(
              'w-full resize-none rounded-lg border border-input bg-background px-3 py-2 text-sm',
              'placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              'min-h-[40px] max-h-[120px]'
            )}
            style={{
              height: 'auto',
              overflow: 'hidden',
            }}
            onInput={(e) => {
              const target = e.target as HTMLTextAreaElement;
              target.style.height = 'auto';
              target.style.height = `${Math.min(target.scrollHeight, 120)}px`;
            }}
          />
        </div>

        <div className="flex gap-1">
          {(isLoading || isStreaming) ? (
            <button
              onClick={handleCancel}
              className={cn(
                'p-2 rounded-lg bg-destructive text-destructive-foreground',
                'hover:bg-destructive/90 transition-colors'
              )}
              title="Cancel"
            >
              <StopCircle className="w-5 h-5" />
            </button>
          ) : (
            <>
              <button
                onClick={() => {/* TODO: Voice input */}}
                className={cn(
                  'p-2 rounded-lg text-muted-foreground',
                  'hover:bg-muted hover:text-foreground transition-colors'
                )}
                title="Voice input"
              >
                <Mic className="w-5 h-5" />
              </button>

              <button
                onClick={handleSubmit}
                disabled={!input.trim()}
                className={cn(
                  'p-2 rounded-lg bg-primary text-primary-foreground',
                  'hover:bg-primary/90 transition-colors',
                  'disabled:opacity-50 disabled:cursor-not-allowed'
                )}
                title="Send message"
              >
                <Send className="w-5 h-5" />
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
