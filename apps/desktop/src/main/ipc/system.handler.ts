import { IpcMain, app, shell, BrowserWindow } from 'electron';
import { platform, homedir, hostname } from 'os';

export function registerSystemHandlers(ipcMain: IpcMain): void {
  // Get system information
  ipcMain.handle('system:info', async () => {
    return {
      platform: platform(),
      homedir: homedir(),
      hostname: hostname(),
      appVersion: app.getVersion(),
      electronVersion: process.versions.electron,
      nodeVersion: process.versions.node,
    };
  });

  // Open external URL
  ipcMain.handle('system:open-external', async (_event, url: string) => {
    await shell.openExternal(url);
    return { success: true };
  });

  // Open file in default application
  ipcMain.handle('system:open-path', async (_event, path: string) => {
    const result = await shell.openPath(path);
    return { success: !result, error: result || undefined };
  });

  // Show item in folder
  ipcMain.handle('system:show-in-folder', async (_event, path: string) => {
    shell.showItemInFolder(path);
    return { success: true };
  });

  // Minimize window
  ipcMain.handle('window:minimize', async (event) => {
    const window = BrowserWindow.fromWebContents(event.sender);
    window?.minimize();
    return { success: true };
  });

  // Maximize/restore window
  ipcMain.handle('window:maximize', async (event) => {
    const window = BrowserWindow.fromWebContents(event.sender);
    if (window?.isMaximized()) {
      window.unmaximize();
    } else {
      window?.maximize();
    }
    return { success: true, maximized: window?.isMaximized() };
  });

  // Close window
  ipcMain.handle('window:close', async (event) => {
    const window = BrowserWindow.fromWebContents(event.sender);
    window?.hide();
    return { success: true };
  });

  // Check if window is maximized
  ipcMain.handle('window:is-maximized', async (event) => {
    const window = BrowserWindow.fromWebContents(event.sender);
    return window?.isMaximized() ?? false;
  });

  // Get app paths
  ipcMain.handle('system:get-path', async (_event, name: string) => {
    try {
      const path = app.getPath(name as Parameters<typeof app.getPath>[0]);
      return { success: true, path };
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  });
}
