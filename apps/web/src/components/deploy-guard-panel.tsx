"use client";

interface Guard { guard: string; description: string; blocking: boolean; passed: boolean; }
interface DeployGuardPanelProps { guards: Guard[]; canDeploy: boolean;
  passed: number; total: number; onDeploy: () => void; }

export function DeployGuardPanel({ guards, canDeploy, passed, total, onDeploy }: DeployGuardPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`flex items-center justify-between p-4 border-b dark:border-gray-700 ${canDeploy ? "bg-green-50 dark:bg-green-900/10" : "bg-red-50 dark:bg-red-900/10"}`}>
        <h3 className="font-semibold text-sm">🛡️ Deploy Guards</h3>
        <div className="flex gap-2">
          <span className="text-xs text-gray-400">{passed}/{total} passed</span>
          <button onClick={onDeploy} disabled={!canDeploy}
            className={`px-3 py-1 text-xs rounded ${canDeploy ? "bg-green-500 text-white" : "bg-gray-300 text-gray-500 cursor-not-allowed"}`}>
            {canDeploy ? "🚀 Deploy" : "🚫 Blocked"}
          </button>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {guards.map(g => (
          <div key={g.guard} className="flex items-center justify-between px-4 py-2 text-xs">
            <div className="flex items-center gap-2">
              <span>{g.passed ? "✅" : "❌"}</span>
              <span>{g.description}</span>
              {g.blocking && !g.passed && <span className="text-red-500 text-[10px]">blocking</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
