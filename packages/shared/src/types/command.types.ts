export type CommandCategory =
  | 'filesystem'
  | 'terminal'
  | 'browser'
  | 'git'
  | 'app_control'
  | 'clipboard'
  | 'notification'
  | 'calendar'
  | 'code_analysis';

export type RiskLevel = 'low' | 'medium' | 'high';

export interface Command {
  id: string;
  category: CommandCategory;
  action: string;
  description: string;
  riskLevel: RiskLevel;
  requiresApproval: boolean;
  parameters: Record<string, unknown>;
  timestamp: Date;
}

export interface CommandResult {
  commandId: string;
  success: boolean;
  output?: string;
  error?: string;
  duration: number;
  timestamp: Date;
}

export interface CommandPlan {
  id: string;
  intent: string;
  commands: Command[];
  confidence: number;
  explanation: string;
}
