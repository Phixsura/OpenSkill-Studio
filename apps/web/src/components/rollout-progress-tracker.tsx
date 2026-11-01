"use client";

interface Rollout { deploymentId: string; currentPct: number; status: string;
  steps: number[]; currentStep: number; }
interface RolloutProgressTrackerProps { rollouts: Rollout[];
  onAdvance: (id: string) => void; onPause: (id: string) => void; }

export function RolloutProgressTracker({ rollouts, onAdvance, onPause }: RolloutProgressTrackerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚀 Rollout Tracker</h3>
        <span className="text-xs text-gray-400">{rollouts.length} rollouts</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {rollouts.map(r => (
          <div key={r.deploymentId} className="px-4 py-3">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-mono">{r.deploymentId}</span>
              <div className="flex gap-2">
                <span className="text-xs font-bold">{r.currentPct}%</span>
                {r.status === "in_progress" && (
                  <>
                    <button onClick={() => onAdvance(r.deploymentId)} className="text-xs text-blue-500">▶</button>
                    <button onClick={() => onPause(r.deploymentId)} className="text-xs text-yellow-500">⏸</button>
                  </>
                )}
              </div>
            </div>
            <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${r.status === "complete" ? "bg-green-500" : r.status === "paused" ? "bg-yellow-500" : "bg-blue-500"}`}
                style={{ width: `${r.currentPct}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
