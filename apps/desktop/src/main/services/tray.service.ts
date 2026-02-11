import { Tray, Menu, nativeImage, BrowserWindow, app, NativeImage } from 'electron';
import { join } from 'path';

export class TrayService {
  private tray: Tray | null = null;
  private mainWindow: BrowserWindow | null;

  constructor(mainWindow: BrowserWindow | null) {
    this.mainWindow = mainWindow;
  }

  create(): void {
    // Create a simple tray icon (you can replace with actual icon)
    const iconPath = join(__dirname, '../../resources/icons/tray-icon.png');

    // Create a fallback icon if the file doesn't exist
    let icon: NativeImage;
    try {
      icon = nativeImage.createFromPath(iconPath);
      if (icon.isEmpty()) {
        // Create a simple 16x16 icon as fallback
        icon = nativeImage.createEmpty();
      }
    } catch {
      icon = nativeImage.createEmpty();
    }

    this.tray = new Tray(icon.isEmpty() ? this.createDefaultIcon() : icon);

    this.tray.setToolTip('Lokai - Desktop AI Assistant');

    const contextMenu = Menu.buildFromTemplate([
      {
        label: 'Show Lokai',
        click: () => {
          this.mainWindow?.show();
          this.mainWindow?.focus();
        },
      },
      {
        label: 'Settings',
        click: () => {
          this.mainWindow?.webContents.send('open-settings');
          this.mainWindow?.show();
        },
      },
      { type: 'separator' },
      {
        label: 'Status',
        enabled: false,
        sublabel: 'Connected',
      },
      { type: 'separator' },
      {
        label: 'Quit Lokai',
        click: () => {
          app.quit();
        },
      },
    ]);

    this.tray.setContextMenu(contextMenu);

    this.tray.on('click', () => {
      if (this.mainWindow?.isVisible()) {
        this.mainWindow.hide();
      } else {
        this.mainWindow?.show();
        this.mainWindow?.focus();
      }
    });
  }

  private createDefaultIcon(): NativeImage {
    // Create a simple 16x16 colored icon as fallback
    const size = 16;
    const canvas = Buffer.alloc(size * size * 4);

    // Fill with a purple color (Lokai brand color)
    for (let i = 0; i < size * size; i++) {
      canvas[i * 4] = 147;     // R
      canvas[i * 4 + 1] = 51;  // G
      canvas[i * 4 + 2] = 234; // B
      canvas[i * 4 + 3] = 255; // A
    }

    return nativeImage.createFromBuffer(canvas, { width: size, height: size });
  }

  updateStatus(status: 'connected' | 'disconnected' | 'processing'): void {
    // Update tray icon based on status
    const tooltip = `Lokai - ${status.charAt(0).toUpperCase() + status.slice(1)}`;
    this.tray?.setToolTip(tooltip);
  }

  destroy(): void {
    this.tray?.destroy();
    this.tray = null;
  }
}
