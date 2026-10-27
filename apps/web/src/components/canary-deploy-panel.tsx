"use client";

interface CanaryDeploy {
  deployId: string; stableVersion: string; canaryVersion: string;
  rolloutPct: number; status: string; errorRate: number; errorThreshold: number;
}

const statusColors: Record<string, string> = {
  active: "text-blue-600", completed: "text-green-600", rolled_back: "text-red-600", promoting: "text-yellow-600",
};

export function CanaryDeployPanel({ deploy, onIncrease, onRollback }: {
  deploy: CanaryDeploy; onIncrease?: (pct: number) => void; onRollback?: () => void;
}) {
  return (
    <div className="border dark:border-gray-700 rounded-xl p-4 space-y-3">
      <div className="flex justify-between items-center">
        <h3 className="font-bold text-sm">Canary Deploy</h3>
        <span className={`text-xs font-medium capitalize ${statusColors[deploy.status] || ""}`}>{deploy.status}</span>
      </div>
      <div className="flex gap-4 text-sm">
        <div className="flex-1 text-center border dark:border-gray-700 rounded-lg p-2">
          <span className="text-xs text-gray-500 block">Stable</span>
          <span className="font-bold">v{deploy.stableVersion}</span>
        </div>
        <div className="flex items-center text-gray-400">→</div>
        <div className="flex-1 text-center border border-blue-300 dark:border-blue-700 rounded-lg p-2 bg-blue-50 dark:bg-blue-900/10">
          <span className="text-xs text-gray-500 block">Canary</span>
          <span className="font-bold">v{deploy.canaryVersion}</span>
        </div>
      </div>
      <div>
        <div className="flex justify-between text-xs mb-1">
          <span>Rollout: {deploy.rolloutPct}%</span>
          <span className={deploy.errorRate > deploy.errorThreshold ? "text-red-500" : "text-green-500"}>
            Errors: {deploy.errorRate.toFixed(1)}% (threshold: {deploy.errorThreshold}%)
          </span>
        </div>
        <div className="h-2.5 bg-gray-100 dark:bg-gray-800 rounded-full">
          <div className="h-full bg-blue-500 rounded-full" style={{ width: `${deploy.rolloutPct}%` }} />
        </div>
      </div>
      {deploy.status === "active" && (
        <div className="flex gap-2">
          <button onClick={() => onIncrease?.(Math.min(100, deploy.rolloutPct + 25))}
            className="flex-1 text-xs bg-blue-500 text-white py-1.5 rounded-lg">Increase +25%</button>
          <button onClick={onRollback} className="flex-1 text-xs bg-red-500 text-white py-1.5 rounded-lg">Rollback</button>
        </div>
      )}
    </div>
  );
}
