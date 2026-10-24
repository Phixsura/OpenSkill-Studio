"use client";
interface RemediationAction { rule: string; severity: string; autoFixed: boolean; }
interface AutoRemediatePanelProps { actions: RemediationAction[]; totalRules: number; actionsTaken: number; }
const SEV_STYLE: Record<string, string> = { critical: "text-red-600", warning: "text-yellow-600", info: "text-blue-500" };
export function AutoRemediatePanel({ actions, totalRules, actionsTaken }: AutoRemediatePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔧 Auto-Remediation</h3>
        <span className="text-xs text-gray-400">{totalRules} rules · {actionsTaken} actions taken</span>
      </div>
      {actions.length > 0 ? (
        <div className="divide-y dark:divide-gray-700">
          {actions.map((a, i) => (
            <div key={i} className="flex justify-between px-4 py-1.5 text-xs">
              <span className="font-mono">{a.rule}</span>
              <div className="flex items-center gap-2">
                <span className={SEV_STYLE[a.severity] ?? ""}>{a.severity}</span>
                <span className="text-green-600">✅ fixed</span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-4 text-xs text-green-600 text-center">No remediation needed</div>
      )}
    </div>
  );
}
