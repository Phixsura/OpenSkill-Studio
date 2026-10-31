"use client";

interface Deployment {
  deployId: string;
  fromVersion: string;
  toVersion: string;
  strategy: "blue_green" | "canary" | "rolling" | "immediate";
  status: "pending" | "in_progress" | "promoting" | "completed" | "rolled_back" | "failed";
  trafficPercent: number;
  healthPassed: boolean;
  error?: string;
  createdAt: string;
}

const strategyIcons: Record<string, string> = {
  blue_green: "🔵🟢", canary: "🐤", rolling: "🔄", immediate: "⚡",
};

const statusConfig: Record<string, { color: string }> = {
  pending: { color: "bg-gray-100 text-gray-600 dark:bg-gray-800" },
  in_progress: { color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30" },
  promoting: { color: "bg-purple-100 text-purple-700 dark:bg-purple-900/30" },
  completed: { color: "bg-green-100 text-green-700 dark:bg-green-900/30" },
  rolled_back: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30" },
  failed: { color: "bg-red-100 text-red-600 dark:bg-red-900/30" },
};

export function DeploymentPanel({
  deployments,
  activeVersion,
  onPromote,
  onRollback,
  onIncreaseTraffic,
}: {
  deployments: Deployment[];
  activeVersion: string;
  onPromote?: (id: string) => void;
  onRollback?: (id: string) => void;
  onIncreaseTraffic?: (id: string, pct: number) => void;
}) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🚀 Deployments</h2>
        <span className="text-sm text-gray-500">Active: <code className="font-bold">{activeVersion}</code></span>
      </div>

      <div className="space-y-3">
        {deployments.map((dep) => {
          const sCfg = statusConfig[dep.status];
          return (
            <div key={dep.deployId} className="rounded-xl border dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span>{strategyIcons[dep.strategy]}</span>
                  <span className="font-mono text-sm">v{dep.fromVersion} → v{dep.toVersion}</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded-full ${sCfg.color}`}>{dep.status.replace("_", " ")}</span>
                </div>
                <div className="flex gap-1">
                  {dep.status === "in_progress" && dep.healthPassed && (
                    <button onClick={() => onPromote?.(dep.deployId)}
                      className="text-xs bg-green-600 text-white px-2 py-1 rounded">Promote</button>
                  )}
                  {(dep.status === "in_progress" || dep.status === "completed") && (
                    <button onClick={() => onRollback?.(dep.deployId)}
                      className="text-xs bg-red-600 text-white px-2 py-1 rounded">Rollback</button>
                  )}
                </div>
              </div>

              {dep.strategy !== "immediate" && (
                <div className="mb-1">
                  <div className="flex justify-between text-xs text-gray-500 mb-0.5">
                    <span>Traffic to new version</span>
                    <span>{dep.trafficPercent}%</span>
                  </div>
                  <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500 rounded-full transition-all" style={{ width: `${dep.trafficPercent}%` }} />
                  </div>
                </div>
              )}

              <div className="flex gap-3 text-xs text-gray-500">
                <span className="capitalize">{dep.strategy.replace("_", "-")}</span>
                <span>{dep.healthPassed ? "✅ Healthy" : "⏳ Checking"}</span>
                <span>{dep.createdAt}</span>
              </div>
              {dep.error && <div className="text-xs text-red-500 mt-1">{dep.error}</div>}
            </div>
          );
        })}
      </div>
    </div>
  );
}
