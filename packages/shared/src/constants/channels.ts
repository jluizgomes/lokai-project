export const IPC_CHANNELS = {
  // Agent communication
  AGENT: {
    SEND_MESSAGE: 'agent:send-message',
    SEND_MESSAGE_STREAMING: 'agent:send-message-streaming',
    STATUS: 'agent:status',
    EXECUTE_TOOL: 'agent:execute-tool',
    CANCEL: 'agent:cancel',
    STREAM_TOKEN: 'agent:stream-token',
    STREAM_COMPLETE: 'agent:stream-complete',
    STREAM_ERROR: 'agent:stream-error',
  },

  // Approval system
  APPROVAL: {
    REQUEST: 'approval:request',
    RESPOND: 'approval:respond',
    LIST: 'approval:list',
    CANCEL: 'approval:cancel',
    SHOW: 'approval:show',
  },

  // System utilities
  SYSTEM: {
    INFO: 'system:info',
    OPEN_EXTERNAL: 'system:open-external',
    OPEN_PATH: 'system:open-path',
    SHOW_IN_FOLDER: 'system:show-in-folder',
    GET_PATH: 'system:get-path',
  },

  // Window controls
  WINDOW: {
    MINIMIZE: 'window:minimize',
    MAXIMIZE: 'window:maximize',
    CLOSE: 'window:close',
    IS_MAXIMIZED: 'window:is-maximized',
  },

  // Events
  EVENTS: {
    FOCUS_INPUT: 'focus-input',
    OPEN_SETTINGS: 'open-settings',
    QUICK_ACTION: 'quick-action',
  },
} as const;

export const JSON_RPC_METHODS = {
  PING: 'ping',
  PROCESS_MESSAGE: 'process_message',
  EXECUTE_TOOL: 'execute_tool',
  CANCEL: 'cancel',
  GET_CONTEXT: 'get_context',
  UPDATE_SETTINGS: 'update_settings',
} as const;

export const TOOL_NAMES = {
  // File system
  FS_READ: 'filesystem_read',
  FS_WRITE: 'filesystem_write',
  FS_DELETE: 'filesystem_delete',
  FS_LIST: 'filesystem_list',
  FS_SEARCH: 'filesystem_search',

  // Terminal
  TERMINAL_READ: 'terminal_read',
  TERMINAL_EXEC: 'terminal_execute',

  // Browser
  BROWSER_NAVIGATE: 'browser_navigate',
  BROWSER_ACTION: 'browser_action',
  BROWSER_READ: 'browser_read',

  // Git
  GIT_STATUS: 'git_status',
  GIT_COMMIT: 'git_commit',
  GIT_PUSH: 'git_push',
  GIT_PULL: 'git_pull',

  // App control
  APP_LAUNCH: 'app_launch',
  APP_CLOSE: 'app_close',
  APP_FOCUS: 'app_focus',

  // Clipboard
  CLIPBOARD_READ: 'clipboard_read',
  CLIPBOARD_WRITE: 'clipboard_write',

  // Notification
  NOTIFICATION_SEND: 'notification_send',

  // Code analysis
  CODE_ANALYZE: 'code_analyze',
  CODE_EXPLAIN: 'code_explain',
} as const;
