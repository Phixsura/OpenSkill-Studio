"use client";

interface Deploy { version: string; environment: string; status: string;
  deployer: string; timestamp: string; durationSec: number; }
interface DeployHistoryListProps { deploys: Deploy[]; successDisplay: string; total: number; }

export function DeployHistoryList({ deploys, successDisplay, total }: DeployHistoryListProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚀 Deploy History</h3>
        <span className="text-xs text-gray-400">{total} deploys · {successDisplay} success</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {deploys.map((d, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-2.5">
            <div className="flex items-center gap-2">
              <span>{d.status === "success" ? "✅" : "❌"}</span>
              <span className="text-sm font-mono">v{d.version}</span>
              <span className="text-xs text-gray-400 capitalize">{d.environment}</span>
            </div>
            <div className="flex gap-3 text-xs text-gray-400">
              <span>{d.deployer}</span>
              <span>{d.durationSec}s</span>
              <span>{d.timestamp}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
