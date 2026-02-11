import { useUIStore } from '../../stores/ui.store';
import { useSettingsStore } from '../../stores/settings.store';
import { cn } from '../../lib/utils';

export function StatusBar() {
  const { agentStatus } = useUIStore();
  const { llm } = useSettingsStore();

  const statusText = {
    connected: 'Connected',
    disconnected: 'Disconnected',
    processing: 'Processing...',
  };

  return (
    <footer className="flex items-center justify-between px-3 py-1.5 bg-card border-t border-border text-xs text-muted-foreground">
      <div className="flex items-center gap-2">
        <div
          className={cn(
            'w-1.5 h-1.5 rounded-full',
            agentStatus === 'connected' && 'bg-green-500',
            agentStatus === 'disconnected' && 'bg-red-500',
            agentStatus === 'processing' && 'bg-yellow-500 animate-pulse'
          )}
        />
        <span>{statusText[agentStatus]}</span>
      </div>

      <div className="flex items-center gap-4">
        <span className="opacity-75">
          {llm.provider}: {llm.model}
        </span>
        <span className="opacity-50">Ctrl+Shift+Space</span>
      </div>
    </footer>
  );
}
