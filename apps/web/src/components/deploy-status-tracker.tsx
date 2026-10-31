"use client";

interface DeployStep { name: string; status: string; durationMs: number; }
interface DeployStatusTrackerProps { deployId: string; version: string;
  environment: string; steps: DeployStep[]; status: string; progress: number; }

const STEP_ICONS: Record<string, string> = {
  completed: "✅", failed: "❌", pending: "⬜", running: "🔄",
};

export function DeployStatusTracker({ deployId, version, environment, steps, status, progress }: DeployStatusTrackerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <div>
          <h3 className="font-semibold text-sm">🚀 Deploy {deployId}</h3>
          <div className="text-[10px] text-gray-400">v{version} → {environment}</div>
        </div>
        <div className="text-right">
          <span className={`text-xs font-medium ${status === "completed" ? "text-green-600" : status === "failed" ? "text-red-500" : "text-blue-500"}`}>{status}</span>
          <div className="text-[10px] text-gray-400">{progress}%</div>
        </div>
      </div>
      <div className="p-4">
        <div className="flex items-center gap-1">
          {steps.map((s, i) => (
            <div key={s.name} className="flex items-center flex-1">
              <div className={`flex-1 text-center py-1.5 rounded text-[10px] ${s.status === "completed" ? "bg-green-100 dark:bg-green-900/20" : s.status === "failed" ? "bg-red-100 dark:bg-red-900/20" : "bg-gray-100 dark:bg-gray-800"}`}>
                {STEP_ICONS[s.status]} {s.name}
                {s.durationMs > 0 && <div className="text-gray-400">{(s.durationMs / 1000).toFixed(1)}s</div>}
              </div>
              {i < steps.length - 1 && <span className="text-gray-300 mx-0.5">→</span>}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
