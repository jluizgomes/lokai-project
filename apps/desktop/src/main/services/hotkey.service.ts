import { globalShortcut, BrowserWindow } from 'electron';

export class HotkeyService {
  private mainWindow: BrowserWindow | null;
  private registeredShortcuts: string[] = [];

  constructor(mainWindow: BrowserWindow | null) {
    this.mainWindow = mainWindow;
  }

  register(): void {
    // Main toggle shortcut: Cmd/Ctrl + Shift + Space
    const toggleShortcut = process.platform === 'darwin'
      ? 'Command+Shift+Space'
      : 'Control+Shift+Space';

    const registered = globalShortcut.register(toggleShortcut, () => {
      this.toggleWindow();
    });

    if (registered) {
      this.registeredShortcuts.push(toggleShortcut);
      console.log(`Hotkey registered: ${toggleShortcut}`);
    } else {
      console.error(`Failed to register hotkey: ${toggleShortcut}`);
    }

    // Quick action shortcut: Cmd/Ctrl + Shift + I
    const quickActionShortcut = process.platform === 'darwin'
      ? 'Command+Shift+I'
      : 'Control+Shift+I';

    const quickActionRegistered = globalShortcut.register(quickActionShortcut, () => {
      this.showAndFocus();
      this.mainWindow?.webContents.send('quick-action');
    });

    if (quickActionRegistered) {
      this.registeredShortcuts.push(quickActionShortcut);
      console.log(`Hotkey registered: ${quickActionShortcut}`);
    }
  }

  private toggleWindow(): void {
    if (!this.mainWindow) return;

    if (this.mainWindow.isVisible()) {
      this.mainWindow.hide();
    } else {
      this.showAndFocus();
    }
  }

  private showAndFocus(): void {
    if (!this.mainWindow) return;

    this.mainWindow.show();
    this.mainWindow.focus();

    // Focus the input field in the renderer
    this.mainWindow.webContents.send('focus-input');
  }

  updateMainWindow(window: BrowserWindow | null): void {
    this.mainWindow = window;
  }

  unregisterAll(): void {
    for (const shortcut of this.registeredShortcuts) {
      globalShortcut.unregister(shortcut);
    }
    this.registeredShortcuts = [];
  }

  isRegistered(shortcut: string): boolean {
    return globalShortcut.isRegistered(shortcut);
  }
}
