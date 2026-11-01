"use client";

interface CanaryDeployStatusProps {
  appId: string; version: string; phase: string;
  trafficPct: number; checksCount: number;
  onAdvance: () => void; onRollback: () => void;
}

const PHASE_STYLE: Record<string, { bg: string; text: string }> = {
  canary: { bg: "bg-yellow-100 dark:bg-yellow-900/20", text: "text-yellow-700 dark:text-yellow-400" },
  promoted: { bg: "bg-green-100 dark:bg-green-900/20", text: "text-green-700 dark:text-green-400" },
  rollback: { bg: "bg-red-100 dark:bg-red-900/20", text: "text-red-700 dark:text-red-400" },
};

export function CanaryDeployStatus({ appId, version, phase, trafficPct, checksCount, onAdvance, onRollback }: CanaryDeployStatusProps) {
  const ps = PHASE_STYLE[phase] || PHASE_STYLE.canary;
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">🐤 Canary Deploy</h3>
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${ps.bg} ${ps.text}`}>{phase}</span>
      </div>
      <div className="grid grid-cols-3 gap-3 mb-4 text-center">
        <div><p className="text-lg font-bold">{appId}</p><p className="text-xs text-gray-400">App</p></div>
        <div><p className="text-lg font-bold">v{version}</p><p className="text-xs text-gray-400">Version</p></div>
        <div><p className="text-lg font-bold">{trafficPct}%</p><p className="text-xs text-gray-400">Traffic</p></div>
      </div>
      <div className="h-3 bg-gray-100 dark:bg-gray-800 rounded-full mb-3 overflow-hidden">
        <div className={`h-full rounded-full transition-all ${phase === "rollback" ? "bg-red-500" : "bg-green-500"}`}
             style={{ width: `${trafficPct}%` }} />
      </div>
      <div className="flex justify-between items-center">
        <span className="text-xs text-gray-400">{checksCount} health checks</span>
        {phase === "canary" && (
          <div className="flex gap-2">
            <button onClick={onRollback} className="text-xs px-3 py-1 border border-red-200 text-red-600 rounded hover:bg-red-50">Rollback</button>
            <button onClick={onAdvance} className="text-xs px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700">Advance</button>
          </div>
        )}
      </div>
    </div>
  );
}
