import { useState } from 'react';
import { X, AlertTriangle, Shield, ShieldCheck, ShieldAlert } from 'lucide-react';
import { ApprovalRequest } from '../../stores/chat.store';
import { cn } from '../../lib/utils';

interface ApprovalModalProps {
  request: ApprovalRequest;
  onClose: () => void;
}

export function ApprovalModal({ request, onClose }: ApprovalModalProps) {
  const [rememberChoice, setRememberChoice] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleApprove = async () => {
    setIsSubmitting(true);
    try {
      await window.iara.approval.respond(request.id, {
        approved: true,
        remember: rememberChoice,
      });
      onClose();
    } catch (error) {
      console.error('Failed to approve:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeny = async () => {
    setIsSubmitting(true);
    try {
      await window.iara.approval.respond(request.id, {
        approved: false,
        remember: rememberChoice,
      });
      onClose();
    } catch (error) {
      console.error('Failed to deny:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const RiskIcon = {
    low: ShieldCheck,
    medium: Shield,
    high: ShieldAlert,
  }[request.riskLevel];

  const riskColors = {
    low: 'text-green-500 bg-green-500/10',
    medium: 'text-yellow-500 bg-yellow-500/10',
    high: 'text-red-500 bg-red-500/10',
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-card rounded-lg shadow-xl w-full max-w-md mx-4 overflow-hidden">
        <div className="flex items-center justify-between p-4 border-b border-border">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-yellow-500" />
            <h2 className="font-semibold">Action Approval Required</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded hover:bg-muted transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-4 space-y-4">
          <div className="flex items-start gap-3">
            <div className={cn('p-2 rounded-lg', riskColors[request.riskLevel])}>
              <RiskIcon className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-medium">{request.action}</h3>
              <p className="text-sm text-muted-foreground mt-1">
                {request.description}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground">Risk Level:</span>
            <span
              className={cn(
                'text-xs font-medium px-2 py-0.5 rounded-full',
                riskColors[request.riskLevel]
              )}
            >
              {request.riskLevel.toUpperCase()}
            </span>
          </div>

          {request.preview && (
            <div className="bg-muted rounded-lg p-3">
              <p className="text-xs text-muted-foreground mb-1">Preview:</p>
              <pre className="text-xs font-mono whitespace-pre-wrap overflow-x-auto">
                {request.preview}
              </pre>
            </div>
          )}

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={rememberChoice}
              onChange={(e) => setRememberChoice(e.target.checked)}
              className="rounded border-input"
            />
            <span className="text-sm text-muted-foreground">
              Remember this choice for similar actions
            </span>
          </label>
        </div>

        <div className="flex gap-2 p-4 border-t border-border bg-muted/50">
          <button
            onClick={handleDeny}
            disabled={isSubmitting}
            className={cn(
              'flex-1 px-4 py-2 rounded-lg text-sm font-medium',
              'bg-muted hover:bg-muted/80 transition-colors',
              'disabled:opacity-50 disabled:cursor-not-allowed'
            )}
          >
            Deny
          </button>
          <button
            onClick={handleApprove}
            disabled={isSubmitting}
            className={cn(
              'flex-1 px-4 py-2 rounded-lg text-sm font-medium',
              'bg-primary text-primary-foreground hover:bg-primary/90 transition-colors',
              'disabled:opacity-50 disabled:cursor-not-allowed'
            )}
          >
            Approve
          </button>
        </div>
      </div>
    </div>
  );
}
