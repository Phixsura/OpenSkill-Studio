"use client";

interface Step { action: string; version?: string; count?: number; timeoutSeconds?: number; }
interface RollbackPlannerProps { currentVersion: string; targetVersion: string;
  steps: Step[]; risk: string; estimatedMinutes: number; }

const RISK_STYLE: Record<string, string> = { low: "text-green-600", medium: "text-yellow-600", high: "text-red-600" };

export function RollbackPlanner({ currentVersion, targetVersion, steps, risk, estimatedMinutes }: RollbackPlannerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏪ Rollback Plan</h3>
        <span className={`text-xs font-bold uppercase ${RISK_STYLE[risk] ?? ""}`}>{risk} risk</span>
      </div>
      <div className="p-4 text-xs space-y-1">
        <div className="text-gray-400">{currentVersion} → {targetVersion} · ~{estimatedMinutes}min</div>
      </div>
      <div className="border-t dark:border-gray-700 divide-y dark:divide-gray-700">
        {steps.map((s, i) => (
          <div key={i} className="flex items-center gap-2 px-4 py-2 text-xs">
            <span className="text-gray-400 w-5">{i + 1}.</span>
            <span className="font-mono">{s.action}</span>
            {s.version && <span className="text-blue-500">{s.version}</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
