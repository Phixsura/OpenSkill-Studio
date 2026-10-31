"use client";

interface RemediationAction { issue: string; action: string; description: string;
  severity: string; autoApprove: boolean; }
interface AutoRemediationPanelProps { actions: RemediationAction[];
  autoPct: number; total: number; }

export function AutoRemediationPanel({ actions, autoPct, total }: AutoRemediationPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🤖 Auto-Remediation</h3>
        <span className="text-xs text-gray-400">{total} actions · {autoPct}% automated</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {actions.map(a => (
          <div key={a.issue} className="flex items-center justify-between px-4 py-2.5">
            <div>
              <div className="text-xs font-medium">{a.issue}</div>
              <div className="text-[10px] text-gray-400">{a.description}</div>
            </div>
            <div className="flex gap-2">
              <span className="text-xs font-mono text-blue-500">{a.action}</span>
              <span className={`text-[10px] ${a.autoApprove ? "text-green-600" : "text-yellow-600"}`}>
                {a.autoApprove ? "auto" : "manual"}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
