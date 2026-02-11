import { FolderOpen, Terminal, Globe, AppWindow, Clipboard, Plus, Trash2 } from 'lucide-react';
import { useSettingsStore } from '../../stores/settings.store';
import { cn } from '../../lib/utils';

const categoryIcons = {
  filesystem: FolderOpen,
  terminal: Terminal,
  browser: Globe,
  app: AppWindow,
  clipboard: Clipboard,
};

const categoryLabels = {
  filesystem: 'File System',
  terminal: 'Terminal',
  browser: 'Browser',
  app: 'Applications',
  clipboard: 'Clipboard',
};

export function PermissionsTab() {
  const {
    permissions,
    updatePermission,
    allowedDirectories,
    addAllowedDirectory,
    removeAllowedDirectory,
  } = useSettingsStore();

  const groupedPermissions = permissions.reduce(
    (acc, permission) => {
      if (!acc[permission.category]) {
        acc[permission.category] = [];
      }
      acc[permission.category].push(permission);
      return acc;
    },
    {} as Record<string, typeof permissions>
  );

  const handleAddDirectory = () => {
    // In a real app, this would open a file picker dialog
    const path = prompt('Enter directory path:');
    if (path) {
      addAllowedDirectory(path);
    }
  };

  return (
    <div className="space-y-6">
      <section>
        <h3 className="font-medium mb-3">Permission Tiers</h3>
        <p className="text-sm text-muted-foreground mb-4">
          Control what actions IARA can perform. Actions requiring approval will prompt
          you before executing.
        </p>

        <div className="space-y-4">
          {Object.entries(groupedPermissions).map(([category, perms]) => {
            const Icon = categoryIcons[category as keyof typeof categoryIcons];
            const label = categoryLabels[category as keyof typeof categoryLabels];

            return (
              <div key={category} className="border border-border rounded-lg p-3">
                <div className="flex items-center gap-2 mb-3">
                  <Icon className="w-4 h-4 text-muted-foreground" />
                  <h4 className="font-medium text-sm">{label}</h4>
                </div>

                <div className="space-y-2">
                  {perms.map((permission) => (
                    <div
                      key={permission.id}
                      className="flex items-center justify-between py-1"
                    >
                      <span className="text-sm capitalize">{permission.action}</span>
                      <div className="flex items-center gap-3">
                        <label className="flex items-center gap-1.5 text-xs text-muted-foreground">
                          <input
                            type="checkbox"
                            checked={permission.requiresApproval}
                            onChange={(e) =>
                              updatePermission(permission.id, {
                                requiresApproval: e.target.checked,
                              })
                            }
                            className="rounded border-input"
                            disabled={!permission.allowed}
                          />
                          Require approval
                        </label>

                        <button
                          onClick={() =>
                            updatePermission(permission.id, {
                              allowed: !permission.allowed,
                            })
                          }
                          className={cn(
                            'px-2 py-0.5 rounded text-xs font-medium transition-colors',
                            permission.allowed
                              ? 'bg-green-500/10 text-green-500'
                              : 'bg-red-500/10 text-red-500'
                          )}
                        >
                          {permission.allowed ? 'Allowed' : 'Blocked'}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </section>

      <section>
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-medium">Allowed Directories</h3>
          <button
            onClick={handleAddDirectory}
            className="flex items-center gap-1 text-xs text-primary hover:underline"
          >
            <Plus className="w-3 h-3" />
            Add Directory
          </button>
        </div>

        <p className="text-sm text-muted-foreground mb-3">
          IARA can only access files in these directories. Add directories you want
          IARA to work with.
        </p>

        {allowedDirectories.length === 0 ? (
          <div className="text-center py-4 text-sm text-muted-foreground border border-dashed border-border rounded-lg">
            No directories added yet
          </div>
        ) : (
          <div className="space-y-2">
            {allowedDirectories.map((dir) => (
              <div
                key={dir}
                className="flex items-center justify-between px-3 py-2 bg-muted rounded-lg"
              >
                <span className="text-sm font-mono truncate">{dir}</span>
                <button
                  onClick={() => removeAllowedDirectory(dir)}
                  className="p-1 text-muted-foreground hover:text-destructive transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
