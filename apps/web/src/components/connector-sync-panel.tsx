"use client";

interface SyncJob {
  id: string;
  sourceConnector: string;
  targetConnector: string;
  direction: "source_to_target" | "target_to_source" | "bidirectional";
  status: "idle" | "syncing" | "completed" | "failed" | "conflict";
  recordsSynced: number;
  recordsFailed: number;
  conflicts: number;
  lastSyncAt?: string;
  error?: string;
}

const statusConfig: Record<string, { color: string; icon: string }> = {
  idle: { color: "bg-gray-100 text-gray-600 dark:bg-gray-800", icon: "⏸" },
  syncing: { color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30", icon: "🔄" },
  completed: { color: "bg-green-100 text-green-700 dark:bg-green-900/30", icon: "✅" },
  failed: { color: "bg-red-100 text-red-600 dark:bg-red-900/30", icon: "❌" },
  conflict: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", icon: "⚠️" },
};

const dirIcons: Record<string, string> = {
  source_to_target: "→", target_to_source: "←", bidirectional: "⇄",
};

export function ConnectorSyncPanel({
  jobs,
  onSync,
  onResolve,
}: {
  jobs: SyncJob[];
  onSync?: (id: string) => void;
  onResolve?: (id: string) => void;
}) {
  const active = jobs.filter((j) => j.status === "syncing").length;
  const totalSynced = jobs.reduce((s, j) => s + j.recordsSynced, 0);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔄 Connector Sync</h2>
        <span className="text-sm text-gray-500">{active} active · {totalSynced.toLocaleString()} synced</span>
      </div>

      <div className="space-y-2">
        {jobs.map((job) => {
          const cfg = statusConfig[job.status];
          return (
            <div key={job.id} className="rounded-xl border dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span>{cfg.icon}</span>
                  <span className="text-sm font-semibold">{job.sourceConnector}</span>
                  <span className="text-gray-400">{dirIcons[job.direction]}</span>
                  <span className="text-sm font-semibold">{job.targetConnector}</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded-full ${cfg.color}`}>{job.status}</span>
                </div>
                <div className="flex gap-1">
                  {(job.status === "idle" || job.status === "completed" || job.status === "failed") && (
                    <button onClick={() => onSync?.(job.id)}
                      className="text-xs bg-blue-600 text-white px-2 py-1 rounded">Sync</button>
                  )}
                  {job.status === "conflict" && (
                    <button onClick={() => onResolve?.(job.id)}
                      className="text-xs bg-yellow-600 text-white px-2 py-1 rounded">Resolve</button>
                  )}
                </div>
              </div>
              <div className="flex gap-4 text-xs text-gray-500">
                <span>✓ {job.recordsSynced} synced</span>
                {job.recordsFailed > 0 && <span className="text-red-500">✗ {job.recordsFailed} failed</span>}
                {job.conflicts > 0 && <span className="text-yellow-600">⚠ {job.conflicts} conflicts</span>}
                {job.lastSyncAt && <span>{job.lastSyncAt}</span>}
              </div>
              {job.error && <div className="text-xs text-red-500 mt-1">{job.error}</div>}
            </div>
          );
        })}
      </div>
    </div>
  );
}
