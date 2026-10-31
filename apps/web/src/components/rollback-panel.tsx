"use client";

interface RollbackRecord {
  id: string;
  fromVersion: string;
  toVersion: string;
  reason: string;
  status: "pending" | "in_progress" | "completed" | "failed" | "rolled_forward";
  initiatedBy: string;
  startedAt: string;
}

const statusConfig: Record<string, { color: string; icon: string }> = {
  pending: { color: "bg-gray-100 text-gray-600 dark:bg-gray-800", icon: "⏳" },
  in_progress: { color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30", icon: "🔄" },
  completed: { color: "bg-green-100 text-green-700 dark:bg-green-900/30", icon: "✅" },
  failed: { color: "bg-red-100 text-red-600 dark:bg-red-900/30", icon: "❌" },
  rolled_forward: { color: "bg-purple-100 text-purple-700 dark:bg-purple-900/30", icon: "⏩" },
};

export function RollbackPanel({
  currentVersion,
  availableVersions,
  history,
  onRollback,
  onRollforward,
}: {
  currentVersion: string;
  availableVersions: string[];
  history: RollbackRecord[];
  onRollback?: (version: string) => void;
  onRollforward?: (id: string) => void;
}) {
  const rollbackTargets = availableVersions.filter((v) => v !== currentVersion);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">⏪ Version Rollback</h2>
        <span className="text-sm">Current: <code className="font-bold">{currentVersion}</code></span>
      </div>

      {rollbackTargets.length > 0 && (
        <div>
          <span className="text-xs text-gray-500 block mb-1">Rollback to:</span>
          <div className="flex flex-wrap gap-1">
            {rollbackTargets.map((v) => (
              <button key={v} onClick={() => onRollback?.(v)}
                className="text-xs border dark:border-gray-600 px-3 py-1.5 rounded-lg hover:bg-yellow-50 dark:hover:bg-yellow-900/10">
                v{v}
              </button>
            ))}
          </div>
        </div>
      )}

      {history.length > 0 && (
        <div>
          <span className="text-sm font-semibold">History</span>
          <div className="mt-1 space-y-2">
            {history.map((r) => {
              const cfg = statusConfig[r.status];
              return (
                <div key={r.id} className="rounded-lg border dark:border-gray-700 p-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span>{cfg.icon}</span>
                      <span className="text-sm font-mono">v{r.fromVersion} → v{r.toVersion}</span>
                      <span className={`text-xs px-1.5 py-0.5 rounded-full ${cfg.color}`}>{r.status}</span>
                    </div>
                    {r.status === "completed" && (
                      <button onClick={() => onRollforward?.(r.id)}
                        className="text-xs bg-purple-600 text-white px-2 py-1 rounded">Rollforward</button>
                    )}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">{r.reason} · by {r.initiatedBy}</div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
