"use client";

interface Deployment {
  id: string;
  version: string;
  environment: "production" | "staging" | "canary";
  status: "success" | "failed" | "rolling_back" | "in_progress";
  deployedBy: string;
  startedAt: string;
  duration: string;
  changes: number;
  rollbackOf?: string;
}

export function DeploymentHistoryPanel({
  deployments,
  onRollback,
  onRedeploy,
}: {
  deployments: Deployment[];
  onRollback?: (id: string) => void;
  onRedeploy?: (id: string) => void;
}) {
  const statusConfig: Record<string, { icon: string; color: string }> = {
    success: { icon: "✅", color: "text-green-500" },
    failed: { icon: "❌", color: "text-red-500" },
    rolling_back: { icon: "🔄", color: "text-orange-500" },
    in_progress: { icon: "⏳", color: "text-blue-500" },
  };

  const envColors: Record<string, string> = {
    production: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300",
    staging: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300",
    canary: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300",
  };

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🚀 Deployment History</h2>

      <div className="space-y-2">
        {deployments.map((dep) => {
          const cfg = statusConfig[dep.status];
          return (
            <div key={dep.id} className="rounded-xl border dark:border-gray-700 p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className={cfg.color}>{cfg.icon}</span>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-bold text-sm">v{dep.version}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${envColors[dep.environment]}`}>
                        {dep.environment}
                      </span>
                      {dep.rollbackOf && (
                        <span className="text-xs text-orange-500">↩ rollback of {dep.rollbackOf}</span>
                      )}
                    </div>
                    <div className="text-xs text-gray-400 mt-0.5">
                      by {dep.deployedBy} · {dep.startedAt} · {dep.duration} · {dep.changes} changes
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  {dep.status === "success" && onRollback && (
                    <button onClick={() => onRollback(dep.id)}
                      className="text-xs text-orange-500 border border-orange-300 dark:border-orange-700 px-2 py-1 rounded">
                      ↩ Rollback
                    </button>
                  )}
                  {dep.status === "failed" && onRedeploy && (
                    <button onClick={() => onRedeploy(dep.id)}
                      className="text-xs text-blue-500 border border-blue-300 dark:border-blue-700 px-2 py-1 rounded">
                      🔄 Redeploy
                    </button>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
