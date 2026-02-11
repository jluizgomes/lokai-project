import { IpcMain, BrowserWindow } from 'electron';

interface ApprovalRequest {
  id: string;
  action: string;
  description: string;
  riskLevel: 'low' | 'medium' | 'high';
  preview?: string;
  metadata?: Record<string, unknown>;
}

interface ApprovalResponse {
  approved: boolean;
  remember?: boolean;
}

const pendingApprovals = new Map<string, {
  request: ApprovalRequest;
  resolve: (response: ApprovalResponse) => void;
  reject: (error: Error) => void;
}>();

export function registerApprovalHandlers(ipcMain: IpcMain): void {
  // Request approval from the user
  ipcMain.handle('approval:request', async (event, request: ApprovalRequest) => {
    const sender = event.sender;

    return new Promise<ApprovalResponse>((resolve, reject) => {
      pendingApprovals.set(request.id, { request, resolve, reject });

      // Send the approval request to the renderer
      sender.send('approval:show', request);

      // Timeout after 5 minutes
      setTimeout(() => {
        if (pendingApprovals.has(request.id)) {
          pendingApprovals.delete(request.id);
          reject(new Error('Approval timeout'));
        }
      }, 300000);
    });
  });

  // Respond to an approval request
  ipcMain.handle('approval:respond', async (_event, id: string, response: ApprovalResponse) => {
    const pending = pendingApprovals.get(id);

    if (!pending) {
      throw new Error(`No pending approval with id: ${id}`);
    }

    pendingApprovals.delete(id);
    pending.resolve(response);

    return { success: true };
  });

  // Get all pending approvals
  ipcMain.handle('approval:list', async () => {
    return Array.from(pendingApprovals.values()).map(({ request }) => request);
  });

  // Cancel a pending approval
  ipcMain.handle('approval:cancel', async (_event, id: string) => {
    const pending = pendingApprovals.get(id);

    if (pending) {
      pendingApprovals.delete(id);
      pending.reject(new Error('Approval cancelled'));
    }

    return { success: true };
  });
}

export function requestApproval(
  window: BrowserWindow,
  request: ApprovalRequest
): Promise<ApprovalResponse> {
  return new Promise((resolve, reject) => {
    pendingApprovals.set(request.id, { request, resolve, reject });
    window.webContents.send('approval:show', request);
  });
}
