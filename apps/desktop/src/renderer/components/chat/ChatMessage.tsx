import ReactMarkdown from 'react-markdown';
import { User, Bot, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';
import { Message } from '../../stores/chat.store';
import { cn, formatTimestamp } from '../../lib/utils';

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const isError = message.status === 'error';
  const isStreaming = message.status === 'streaming';

  return (
    <div
      className={cn(
        'flex gap-3',
        isUser ? 'flex-row-reverse' : 'flex-row'
      )}
    >
      <div
        className={cn(
          'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
          isUser ? 'bg-primary text-primary-foreground' : 'bg-muted'
        )}
      >
        {isUser ? (
          <User className="w-4 h-4" />
        ) : (
          <Bot className="w-4 h-4" />
        )}
      </div>

      <div
        className={cn(
          'flex flex-col max-w-[80%]',
          isUser ? 'items-end' : 'items-start'
        )}
      >
        <div
          className={cn(
            'rounded-lg px-4 py-2',
            isUser
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted text-foreground',
            isError && 'bg-destructive/10 border border-destructive'
          )}
        >
          {isUser ? (
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          )}

          {isStreaming && (
            <span className="inline-block w-2 h-4 bg-current animate-pulse ml-1" />
          )}
        </div>

        {message.toolCalls && message.toolCalls.length > 0 && (
          <div className="mt-2 space-y-1">
            {message.toolCalls.map((tool, index) => (
              <div
                key={index}
                className="flex items-center gap-2 text-xs text-muted-foreground"
              >
                {tool.status === 'pending' && (
                  <Loader2 className="w-3 h-3 animate-spin" />
                )}
                {tool.status === 'running' && (
                  <Loader2 className="w-3 h-3 animate-spin text-primary" />
                )}
                {tool.status === 'complete' && (
                  <CheckCircle className="w-3 h-3 text-green-500" />
                )}
                {tool.status === 'error' && (
                  <AlertCircle className="w-3 h-3 text-destructive" />
                )}
                <span>{tool.name}</span>
              </div>
            ))}
          </div>
        )}

        <span className="text-xs text-muted-foreground mt-1">
          {formatTimestamp(message.timestamp)}
        </span>
      </div>
    </div>
  );
}
