import { IpcMain } from 'electron';
import { PythonAgentService } from '../services/python-agent.service';

export function registerCommandHandlers(
  ipcMain: IpcMain,
  pythonAgent: PythonAgentService | null
): void {
  // Send a message to the AI agent
  ipcMain.handle('agent:send-message', async (_event, message: string) => {
    if (!pythonAgent?.running) {
      throw new Error('Python agent not running');
    }

    try {
      const response = await pythonAgent.call('process_message', { message });
      return response;
    } catch (error) {
      console.error('Error processing message:', error);
      throw error;
    }
  });

  // Send a message with streaming response
  ipcMain.handle('agent:send-message-streaming', async (event, message: string) => {
    if (!pythonAgent?.running) {
      throw new Error('Python agent not running');
    }

    const sender = event.sender;

    return new Promise((resolve, reject) => {
      pythonAgent.callWithStreaming(
        'process_message',
        { message },
        {
          onToken: (token) => {
            sender.send('agent:stream-token', token);
          },
          onComplete: (response) => {
            sender.send('agent:stream-complete', response);
            resolve(response);
          },
          onError: (error) => {
            sender.send('agent:stream-error', error.message);
            reject(error);
          },
        }
      );
    });
  });

  // Get agent status
  ipcMain.handle('agent:status', async () => {
    return {
      running: pythonAgent?.running ?? false,
    };
  });

  // Execute a tool directly
  ipcMain.handle('agent:execute-tool', async (_event, toolName: string, params: unknown) => {
    if (!pythonAgent?.running) {
      throw new Error('Python agent not running');
    }

    try {
      const response = await pythonAgent.call('execute_tool', { tool: toolName, params });
      return response;
    } catch (error) {
      console.error(`Error executing tool ${toolName}:`, error);
      throw error;
    }
  });

  // Cancel current operation
  ipcMain.handle('agent:cancel', async () => {
    if (!pythonAgent?.running) {
      return { success: false, message: 'Agent not running' };
    }

    try {
      await pythonAgent.call('cancel', {});
      return { success: true };
    } catch (error) {
      console.error('Error canceling operation:', error);
      throw error;
    }
  });
}
