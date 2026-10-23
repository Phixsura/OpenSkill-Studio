"use client";

interface CanaryDeployCardProps { service: string; baseline: string; canary: string;
  trafficPct: number; phase: string; status: string; healthy: boolean;
  onAdvance: () => void; onRollback: () => void; onPromote: () => void; }

const PHASE_COLORS: Record<string, string> = {
  initial: "bg-blue-100 text-blue-700", expanding: "bg-yellow-100 text-yellow-700",
  majority: "bg-purple-100 text-purple-700", complete: "bg-green-100 text-green-700",
};

export function CanaryDeployCard({ service, baseline, canary, trafficPct, phase, status, healthy, onAdvance, onRollback, onPromote }: CanaryDeployCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <div>
          <h3 className="font-semibold text-sm">🐤 Canary: {service}</h3>
          <div className="text-xs text-gray-400 mt-0.5">v{baseline} → v{canary}</div>
        </div>
        <span className={`px-2 py-0.5 text-[10px] rounded-full ${PHASE_COLORS[phase] ?? ""}`}>{phase}</span>
      </div>
      <div className="p-4">
        <div className="flex justify-between text-xs mb-1">
          <span>Canary traffic</span>
          <span className="font-bold">{trafficPct}%</span>
        </div>
        <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden flex">
          <div className="h-full bg-yellow-500" style={{ width: `${trafficPct}%` }} />
          <div className="h-full bg-blue-500 flex-1" />
        </div>
        <div className="flex justify-between text-[10px] text-gray-400 mt-1">
          <span>🐤 v{canary} ({trafficPct}%)</span>
          <span>v{baseline} ({100 - trafficPct}%)</span>
        </div>
      </div>
      <div className="flex gap-2 p-3 border-t dark:border-gray-700">
        {status === "running" && (
          <>
            <button onClick={onAdvance} className="flex-1 py-1.5 text-xs bg-blue-500 text-white rounded-lg">Advance</button>
            <button onClick={onPromote} className="flex-1 py-1.5 text-xs bg-green-500 text-white rounded-lg">Promote</button>
            <button onClick={onRollback} className="flex-1 py-1.5 text-xs bg-red-500 text-white rounded-lg">Rollback</button>
          </>
        )}
      </div>
    </div>
  );
}
