"use client";

interface Deployment { deployment_id: string; version: string; environment: string;
  deployed_by: string; status: string; started_at: string; duration_sec: number | null; }
interface DeploymentHistoryListProps { deployments: Deployment[]; successRate: number;
  avgDurationSec: number; }

const statusStyle: Record<string, { icon: string; color: string }> = {
  success: { icon: "✅", color: "text-green-600" },
  failed: { icon: "❌", color: "text-red-600" },
  in_progress: { icon: "⏳", color: "text-blue-600" },
  rolled_back: { icon: "⏪", color: "text-yellow-600" },
};

const envBadge: Record<string, string> = {
  production: "bg-red-100 text-red-700 dark:bg-red-900/30",
  staging: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30",
  development: "bg-blue-100 text-blue-700 dark:bg-blue-900/30",
};

export function DeploymentHistoryList({ deployments, successRate, avgDurationSec }: DeploymentHistoryListProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Deployments</h2>
        <div className="flex gap-3 text-xs text-gray-400">
          <span>{successRate}% success</span>
          <span>~{avgDurationSec}s avg</span>
        </div>
      </div>
      <div className="space-y-1.5">
        {deployments.map(d => {
          const s = statusStyle[d.status] ?? statusStyle.in_progress;
          return (
            <div key={d.deployment_id} className="flex items-center justify-between rounded border px-3 py-2 dark:border-gray-700">
              <div className="flex items-center gap-2">
                <span>{s.icon}</span>
                <span className="font-mono text-sm font-bold">v{d.version}</span>
                <span className={`rounded-full px-1.5 py-0.5 text-[10px] ${envBadge[d.environment] ?? ""}`}>{d.environment}</span>
              </div>
              <div className="text-right text-xs text-gray-400">
                <p>{d.deployed_by}</p>
                <p>{d.duration_sec ? `${d.duration_sec}s` : "—"}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
