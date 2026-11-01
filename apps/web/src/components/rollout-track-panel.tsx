"use client";

interface RolloutInfo { name: string; currentPct: number; targetPct: number; status: string; stepsCompleted: number; }
interface RolloutTrackPanelProps { rollouts: RolloutInfo[]; }

const STATUS_STYLE: Record<string, string> = {
  in_progress: "text-blue-500", completed: "text-green-600", paused: "text-yellow-600", rolled_back: "text-red-500",
};

export function RolloutTrackPanel({ rollouts }: RolloutTrackPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚀 Rollouts</h3>
        <span className="text-xs text-gray-400">{rollouts.length} active</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {rollouts.map(r => (
          <div key={r.name} className="px-4 py-2">
            <div className="flex justify-between text-xs mb-1">
              <span className="font-semibold">{r.name}</span>
              <span className={STATUS_STYLE[r.status] ?? ""}>{r.status} · {r.currentPct}%/{r.targetPct}%</span>
            </div>
            <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${r.status === "rolled_back" ? "bg-red-500" : "bg-blue-500"}`}
                style={{ width: `${r.currentPct}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
