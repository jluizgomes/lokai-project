import { TrendingUp, Clock, Zap, RefreshCw } from 'lucide-react';

export function LearningDashboard() {
  // Placeholder data - in a real app, this would come from the backend
  const stats = {
    totalPatterns: 0,
    actionsLearned: 0,
    suggestionsAccepted: 0,
    timesSaved: '0h',
  };

  const recentPatterns = [
    // Placeholder for when learning is implemented
  ];

  return (
    <div className="space-y-6">
      <section>
        <h3 className="font-medium mb-3">Learning Dashboard</h3>
        <p className="text-sm text-muted-foreground mb-4">
          Lokai learns from your patterns to provide smarter suggestions over time.
          This dashboard shows what patterns have been detected.
        </p>

        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 rounded-lg bg-muted">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <TrendingUp className="w-4 h-4" />
              <span className="text-xs">Patterns Detected</span>
            </div>
            <p className="text-2xl font-bold">{stats.totalPatterns}</p>
          </div>

          <div className="p-3 rounded-lg bg-muted">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <Zap className="w-4 h-4" />
              <span className="text-xs">Actions Learned</span>
            </div>
            <p className="text-2xl font-bold">{stats.actionsLearned}</p>
          </div>

          <div className="p-3 rounded-lg bg-muted">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <RefreshCw className="w-4 h-4" />
              <span className="text-xs">Suggestions Accepted</span>
            </div>
            <p className="text-2xl font-bold">{stats.suggestionsAccepted}</p>
          </div>

          <div className="p-3 rounded-lg bg-muted">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <Clock className="w-4 h-4" />
              <span className="text-xs">Time Saved</span>
            </div>
            <p className="text-2xl font-bold">{stats.timesSaved}</p>
          </div>
        </div>
      </section>

      <section>
        <h3 className="font-medium mb-3">Recent Patterns</h3>

        {recentPatterns.length === 0 ? (
          <div className="text-center py-8 text-sm text-muted-foreground border border-dashed border-border rounded-lg">
            <p>No patterns detected yet</p>
            <p className="text-xs mt-1">
              Patterns will appear here as you use Lokai
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {/* Pattern items would go here */}
          </div>
        )}
      </section>

      <section>
        <h3 className="font-medium mb-3">Learning Settings</h3>

        <div className="space-y-3">
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              defaultChecked
              className="rounded border-input"
            />
            <div>
              <span className="text-sm">Enable pattern learning</span>
              <p className="text-xs text-muted-foreground">
                Allow Lokai to detect and learn from your usage patterns
              </p>
            </div>
          </label>

          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              defaultChecked
              className="rounded border-input"
            />
            <div>
              <span className="text-sm">Show proactive suggestions</span>
              <p className="text-xs text-muted-foreground">
                Get suggestions based on detected patterns
              </p>
            </div>
          </label>

          <button className="text-sm text-destructive hover:underline">
            Clear all learned patterns
          </button>
        </div>
      </section>
    </div>
  );
}
