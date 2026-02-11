import { Minus, Square, X, Settings } from 'lucide-react';
import { useUIStore } from '../../stores/ui.store';
import { cn } from '../../lib/utils';

export function Header() {
  const { setShowSettings, agentStatus } = useUIStore();

  const handleMinimize = () => {
    window.lokai.window.minimize();
  };

  const handleMaximize = () => {
    window.lokai.window.maximize();
  };

  const handleClose = () => {
    window.lokai.window.close();
  };

  return (
    <header className="drag-region flex items-center justify-between px-4 py-2 bg-card border-b border-border">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <div
            className={cn(
              'w-2 h-2 rounded-full',
              agentStatus === 'connected' && 'bg-green-500',
              agentStatus === 'disconnected' && 'bg-red-500',
              agentStatus === 'processing' && 'bg-yellow-500 animate-pulse'
            )}
          />
          <span className="text-sm font-semibold text-foreground">Lokai</span>
        </div>
      </div>

      <div className="no-drag flex items-center gap-1">
        <button
          onClick={() => setShowSettings(true)}
          className="p-1.5 rounded hover:bg-muted transition-colors"
          title="Settings"
        >
          <Settings className="w-4 h-4 text-muted-foreground" />
        </button>

        <button
          onClick={handleMinimize}
          className="p-1.5 rounded hover:bg-muted transition-colors"
          title="Minimize"
        >
          <Minus className="w-4 h-4 text-muted-foreground" />
        </button>

        <button
          onClick={handleMaximize}
          className="p-1.5 rounded hover:bg-muted transition-colors"
          title="Maximize"
        >
          <Square className="w-3.5 h-3.5 text-muted-foreground" />
        </button>

        <button
          onClick={handleClose}
          className="p-1.5 rounded hover:bg-destructive hover:text-destructive-foreground transition-colors"
          title="Close"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
}
