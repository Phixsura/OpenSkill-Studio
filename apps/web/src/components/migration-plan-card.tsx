"use client";

interface MigrationStep { action: string; table: string; description: string; estimatedSec: number; breaking: boolean; }
interface MigrationPlanCardProps { current: string; target: string; steps: MigrationStep[];
  risk: string; requiresDowntime: boolean; estimatedSec: number; }

const RISK_COLORS: Record<string, string> = { low: "text-green-600", medium: "text-yellow-600", high: "text-red-600" };

export function MigrationPlanCard({ current, target, steps, risk, requiresDowntime, estimatedSec }: MigrationPlanCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-sm">🔄 Migration Plan</h3>
          <span className={`text-xs font-medium uppercase ${RISK_COLORS[risk] ?? ""}`}>{risk} risk</span>
        </div>
        <div className="text-xs text-gray-400 mt-1">
          v{current} → v{target} · {steps.length} steps · ~{estimatedSec}s
          {requiresDowntime && <span className="text-red-500 ml-2">⚠ downtime required</span>}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {steps.map((s, i) => (
          <div key={i} className="flex items-center gap-2 px-4 py-2.5 text-xs">
            <span className="w-5 h-5 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-[10px]">{i + 1}</span>
            <span className="font-mono">{s.action}</span>
            <span className="text-gray-400">{s.table}</span>
            <span className="text-gray-400 ml-auto">{s.description}</span>
            {s.breaking && <span className="text-red-500">⚠</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
