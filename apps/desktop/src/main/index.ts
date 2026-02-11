import { app, BrowserWindow, globalShortcut, ipcMain } from 'electron';
import { join } from 'path';
import { TrayService } from './services/tray.service';
import { HotkeyService } from './services/hotkey.service';
import { PythonAgentService } from './services/python-agent.service';
import { registerIpcHandlers } from './ipc';
import { createMainWindow } from './window/main.window';

let mainWindow: BrowserWindow | null = null;
let trayService: TrayService | null = null;
let hotkeyService: HotkeyService | null = null;
let pythonAgentService: PythonAgentService | null = null;

const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;

async function createWindow() {
  mainWindow = createMainWindow(isDev);

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(join(__dirname, '../renderer/index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  mainWindow.on('close', (event) => {
    if (process.platform === 'darwin') {
      event.preventDefault();
      mainWindow?.hide();
    }
  });

  return mainWindow;
}

async function initializeServices() {
  // Initialize Python Agent Service
  pythonAgentService = new PythonAgentService();
  await pythonAgentService.start();

  // Initialize Tray Service
  trayService = new TrayService(mainWindow);
  trayService.create();

  // Initialize Hotkey Service
  hotkeyService = new HotkeyService(mainWindow);
  hotkeyService.register();

  // Register IPC Handlers
  registerIpcHandlers(ipcMain, pythonAgentService);
}

app.whenReady().then(async () => {
  await createWindow();
  await initializeServices();

  app.on('activate', async () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      await createWindow();
    } else {
      mainWindow?.show();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('will-quit', () => {
  globalShortcut.unregisterAll();
  pythonAgentService?.stop();
});

app.on('before-quit', () => {
  pythonAgentService?.stop();
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

export { mainWindow, pythonAgentService };
