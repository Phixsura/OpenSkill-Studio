"use client";

interface Deploy { id: string; version: string; environment: string; status: string;
  deployedAt: string; deployer: string; commit: string; durationS: number;
  isCurrent: boolean; canRollback: boolean; }
interface DeployHistoryTableProps { deploys: Deploy[]; successRate: number;
  avgDurationS: number; onRollback: (id: string) => void; }

export function DeployHistoryTable({ deploys, successRate, avgDurationS, onRollback }: DeployHistoryTableProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Deploy History</h3>
        <div className="flex gap-3 text-xs text-gray-400">
          <span>{successRate}% success</span>
          <span>avg {avgDurationS}s</span>
        </div>
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {deploys.map(d => (
          <div key={d.id} className="flex items-center justify-between px-4 py-2.5">
            <div className="flex items-center gap-3">
              <span className={d.status === "success" ? "text-green-600" : "text-red-600"}>
                {d.status === "success" ? "✓" : "✗"}
              </span>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold">v{d.version}</span>
                  {d.isCurrent && <span className="rounded bg-blue-100 px-1.5 py-0.5 text-xs text-blue-700 dark:bg-blue-900/30">Current</span>}
                </div>
                <p className="text-xs text-gray-400">{d.deployer} · {d.commit} · {d.durationS}s</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <time className="text-xs text-gray-400">{d.deployedAt}</time>
              {d.canRollback && (
                <button onClick={() => onRollback(d.id)} className="text-xs text-blue-600 hover:underline">Rollback</button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
