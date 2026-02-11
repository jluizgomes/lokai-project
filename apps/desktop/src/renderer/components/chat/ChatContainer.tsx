import { useRef, useEffect } from 'react';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { useChatStore } from '../../stores/chat.store';
import { useUIStore } from '../../stores/ui.store';

export function ChatContainer() {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { messages, isLoading, isStreaming, currentStreamingMessage } = useChatStore();
  const { setAgentStatus } = useUIStore();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, currentStreamingMessage]);

  useEffect(() => {
    // Check agent status on mount
    window.lokai.agent.getStatus().then((status) => {
      setAgentStatus(status.running ? 'connected' : 'disconnected');
    });
  }, [setAgentStatus]);

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground">
            <div className="text-4xl mb-4">🤖</div>
            <h2 className="text-lg font-semibold mb-2">Welcome to Lokai</h2>
            <p className="text-sm max-w-xs">
              Your Intelligent Adaptive Runtime Assistant. Ask me to help with
              files, terminal commands, browser automation, and more.
            </p>
          </div>
        )}

        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {isStreaming && currentStreamingMessage && (
          <ChatMessage
            message={{
              id: 'streaming',
              role: 'assistant',
              content: currentStreamingMessage,
              timestamp: new Date(),
              status: 'streaming',
            }}
          />
        )}

        {isLoading && !isStreaming && (
          <div className="flex items-center gap-2 text-muted-foreground">
            <div className="flex gap-1">
              <span className="typing-dot w-2 h-2 bg-primary rounded-full" />
              <span className="typing-dot w-2 h-2 bg-primary rounded-full" />
              <span className="typing-dot w-2 h-2 bg-primary rounded-full" />
            </div>
            <span className="text-sm">Thinking...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <ChatInput />
    </div>
  );
}
