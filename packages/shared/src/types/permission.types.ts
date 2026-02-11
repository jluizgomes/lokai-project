export type PermissionTier = 'read' | 'write' | 'execute';

export type PermissionCategory =
  | 'filesystem'
  | 'terminal'
  | 'browser'
  | 'app'
  | 'clipboard';

export interface Permission {
  id: string;
  category: PermissionCategory;
  action: string;
  tier: PermissionTier;
  allowed: boolean;
  requiresApproval: boolean;
  paths?: string[];
  commands?: string[];
  createdAt: Date;
  updatedAt: Date;
}

export interface ApprovalRequest {
  id: string;
  action: string;
  description: string;
  riskLevel: 'low' | 'medium' | 'high';
  preview?: string;
  metadata?: Record<string, unknown>;
  timestamp: Date;
  expiresAt: Date;
}

export interface ApprovalResponse {
  requestId: string;
  approved: boolean;
  remember: boolean;
  respondedAt: Date;
}

export interface AllowedDirectory {
  path: string;
  permissions: PermissionTier[];
  addedAt: Date;
}

export interface AllowedCommand {
  pattern: string;
  description: string;
  riskLevel: 'low' | 'medium' | 'high';
  addedAt: Date;
}
