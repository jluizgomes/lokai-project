import { IpcMain } from 'electron';
import { PythonAgentService } from '../services/python-agent.service';
import { registerCommandHandlers } from './command.handler';
import { registerApprovalHandlers } from './approval.handler';
import { registerSystemHandlers } from './system.handler';

export function registerIpcHandlers(
  ipcMain: IpcMain,
  pythonAgent: PythonAgentService | null
): void {
  registerCommandHandlers(ipcMain, pythonAgent);
  registerApprovalHandlers(ipcMain);
  registerSystemHandlers(ipcMain);
}
