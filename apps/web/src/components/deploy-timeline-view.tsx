"use client";

interface Deploy { environment: string; status: string; version?: string; }
interface DeployTimelineViewProps { deploys: Deploy[]; total: number;
  successRate: number; avgDurationSec: number; byEnvironment: Record<string, number>; }

const STATUS_ICONS: Record<string, string> = { success: "✅", failed: "❌", rollback: "⏪", running: "🔄" };

export function DeployTimelineView({ deploys, total, successRate, avgDurationSec, byEnvironment }: DeployTimelineViewProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚀 Deploy Timeline</h3>
        <span className="text-xs text-gray-400">{total} deploys · {successRate}% success · avg {avgDurationSec}s</span>
      </div>
      <div className="flex gap-2 px-4 py-1.5 border-b dark:border-gray-700 text-[10px]">
        {Object.entries(byEnvironment).map(([env, count]) => (
          <span key={env} className="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 rounded">{env}: {count}</span>
        ))}
      </div>
      <div className="divide-y dark:divide-gray-700 max-h-40 overflow-y-auto">
        {deploys.map((d, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span>{STATUS_ICONS[d.status] ?? "⚪"}</span>
              <span>{d.version && `v${d.version}`}</span>
            </div>
            <span className="text-gray-400">{d.environment}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
