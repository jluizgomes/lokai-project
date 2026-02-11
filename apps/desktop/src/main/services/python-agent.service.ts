import { ChildProcess, spawn } from 'child_process';
import { join } from 'path';
import { app } from 'electron';
import { EventEmitter } from 'events';

interface JsonRpcRequest {
  jsonrpc: '2.0';
  id: number;
  method: string;
  params?: unknown;
}

interface JsonRpcResponse {
  jsonrpc: '2.0';
  id: number;
  result?: unknown;
  error?: {
    code: number;
    message: string;
    data?: unknown;
  };
}

interface StreamingCallback {
  onToken: (token: string) => void;
  onComplete: (response: string) => void;
  onError: (error: Error) => void;
}

export class PythonAgentService extends EventEmitter {
  private process: ChildProcess | null = null;
  private requestId = 0;
  private pendingRequests: Map<number, {
    resolve: (value: unknown) => void;
    reject: (error: Error) => void;
    streaming?: StreamingCallback;
  }> = new Map();
  private buffer = '';
  private isRunning = false;

  async start(): Promise<void> {
    if (this.isRunning) {
      console.log('Python agent already running');
      return;
    }

    const isDev = !app.isPackaged;
    const agentPath = isDev
      ? join(__dirname, '../../../../agent')
      : join(process.resourcesPath, 'agent');

    const pythonPath = isDev
      ? join(agentPath, '.venv/bin/python')
      : 'python3';

    console.log('Starting Python agent from:', agentPath);

    try {
      this.process = spawn(pythonPath, ['-m', 'iara_agent.main'], {
        cwd: agentPath,
        stdio: ['pipe', 'pipe', 'pipe'],
        env: {
          ...process.env,
          PYTHONUNBUFFERED: '1',
        },
      });

      this.isRunning = true;

      this.process.stdout?.on('data', (data: Buffer) => {
        this.handleStdout(data.toString());
      });

      this.process.stderr?.on('data', (data: Buffer) => {
        console.error('Python agent stderr:', data.toString());
        this.emit('error', data.toString());
      });

      this.process.on('close', (code) => {
        console.log(`Python agent exited with code ${code}`);
        this.isRunning = false;
        this.emit('close', code);
      });

      this.process.on('error', (error) => {
        console.error('Python agent error:', error);
        this.isRunning = false;
        this.emit('error', error);
      });

      // Wait for the agent to be ready
      await this.waitForReady();
      console.log('Python agent started successfully');
    } catch (error) {
      console.error('Failed to start Python agent:', error);
      this.isRunning = false;
      throw error;
    }
  }

  private async waitForReady(): Promise<void> {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error('Python agent startup timeout'));
      }, 30000);

      const checkReady = async () => {
        try {
          await this.call('ping', {});
          clearTimeout(timeout);
          resolve();
        } catch {
          setTimeout(checkReady, 500);
        }
      };

      setTimeout(checkReady, 1000);
    });
  }

  private handleStdout(data: string): void {
    this.buffer += data;

    // Process complete JSON lines
    const lines = this.buffer.split('\n');
    this.buffer = lines.pop() || '';

    for (const line of lines) {
      if (!line.trim()) continue;

      try {
        const response = JSON.parse(line) as JsonRpcResponse & {
          streaming?: boolean;
          token?: string;
          complete?: boolean;
        };

        if (response.streaming && response.token !== undefined) {
          // Handle streaming token
          const pending = this.pendingRequests.get(response.id);
          if (pending?.streaming) {
            pending.streaming.onToken(response.token);
          }
        } else if (response.complete) {
          // Handle streaming complete
          const pending = this.pendingRequests.get(response.id);
          if (pending?.streaming) {
            pending.streaming.onComplete(response.result as string);
            this.pendingRequests.delete(response.id);
          }
        } else {
          // Handle regular response
          const pending = this.pendingRequests.get(response.id);
          if (pending) {
            if (response.error) {
              pending.reject(new Error(response.error.message));
            } else {
              pending.resolve(response.result);
            }
            this.pendingRequests.delete(response.id);
          }
        }
      } catch (error) {
        console.error('Failed to parse JSON-RPC response:', line, error);
      }
    }
  }

  async call(method: string, params?: unknown): Promise<unknown> {
    if (!this.process || !this.isRunning) {
      throw new Error('Python agent not running');
    }

    const id = ++this.requestId;
    const request: JsonRpcRequest = {
      jsonrpc: '2.0',
      id,
      method,
      params,
    };

    return new Promise((resolve, reject) => {
      this.pendingRequests.set(id, { resolve, reject });

      const requestStr = JSON.stringify(request) + '\n';
      this.process?.stdin?.write(requestStr);

      // Timeout after 60 seconds
      setTimeout(() => {
        if (this.pendingRequests.has(id)) {
          this.pendingRequests.delete(id);
          reject(new Error('Request timeout'));
        }
      }, 60000);
    });
  }

  async callWithStreaming(
    method: string,
    params: unknown,
    callbacks: StreamingCallback
  ): Promise<void> {
    if (!this.process || !this.isRunning) {
      callbacks.onError(new Error('Python agent not running'));
      return;
    }

    const id = ++this.requestId;
    const request: JsonRpcRequest = {
      jsonrpc: '2.0',
      id,
      method,
      params: { ...params as object, streaming: true },
    };

    this.pendingRequests.set(id, {
      resolve: () => {},
      reject: (error) => callbacks.onError(error),
      streaming: callbacks,
    });

    const requestStr = JSON.stringify(request) + '\n';
    this.process?.stdin?.write(requestStr);
  }

  stop(): void {
    if (this.process) {
      this.process.kill();
      this.process = null;
      this.isRunning = false;
    }
  }

  get running(): boolean {
    return this.isRunning;
  }
}
