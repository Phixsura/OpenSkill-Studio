"use client";

interface CanaryDeploymentCardProps {
  stableVersion: string; canaryVersion: string; canaryPct: number;
  status: string; recommendation: string;
  onPromote: () => void; onRollback: () => void;
}

export function CanaryDeploymentCard({ stableVersion, canaryVersion, canaryPct, status, recommendation, onPromote, onRollback }: CanaryDeploymentCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">Canary Deployment</h3>
      <div className="mt-3 flex items-center gap-4">
        <div className="flex-1">
          <p className="text-xs text-gray-400">Stable</p>
          <p className="font-mono text-sm">{stableVersion} ({100 - canaryPct}%)</p>
        </div>
        <div className="flex-1">
          <p className="text-xs text-gray-400">Canary</p>
          <p className="font-mono text-sm">{canaryVersion} ({canaryPct}%)</p>
        </div>
      </div>
      <div className="mt-2 h-3 flex rounded-full overflow-hidden">
        <div className="bg-blue-500" style={{ width: `${100 - canaryPct}%` }} />
        <div className="bg-yellow-500" style={{ width: `${canaryPct}%` }} />
      </div>
      <div className="mt-3 flex items-center justify-between">
        <span className={`text-xs ${recommendation === "promote" ? "text-green-600" : recommendation === "rollback" ? "text-red-600" : "text-yellow-600"}`}>
          💡 {recommendation}
        </span>
        <div className="flex gap-2">
          <button onClick={onRollback} className="rounded border px-2 py-1 text-xs text-red-600">Rollback</button>
          <button onClick={onPromote} className="rounded bg-green-600 px-2 py-1 text-xs text-white">Promote</button>
        </div>
      </div>
    </div>
  );
}
