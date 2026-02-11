import { BrowserWindow, screen } from 'electron';
import { join } from 'path';

export function createMainWindow(_isDev: boolean): BrowserWindow {
  const { width: screenWidth } = screen.getPrimaryDisplay().workAreaSize;

  const windowWidth = 400;
  const windowHeight = 600;

  const mainWindow = new BrowserWindow({
    width: windowWidth,
    height: windowHeight,
    x: screenWidth - windowWidth - 20,
    y: 20,
    minWidth: 350,
    minHeight: 400,
    maxWidth: 600,
    maxHeight: 800,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    resizable: true,
    skipTaskbar: false,
    show: false,
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
    },
  });

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Prevent window from being destroyed on close (hide instead)
  mainWindow.on('close', (event) => {
    if (!mainWindow.isDestroyed()) {
      event.preventDefault();
      mainWindow.hide();
    }
  });

  return mainWindow;
}

export function createSettingsWindow(parentWindow: BrowserWindow | null): BrowserWindow {
  const settingsWindow = new BrowserWindow({
    width: 700,
    height: 500,
    parent: parentWindow || undefined,
    modal: true,
    show: false,
    frame: true,
    resizable: false,
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
    },
  });

  settingsWindow.once('ready-to-show', () => {
    settingsWindow.show();
  });

  return settingsWindow;
}
