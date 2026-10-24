"use client";

interface Experiment { name: string; target: string; faultType: string; status: string; blastRadius: string; }
interface ChaosSchedPanelProps { experiments: Experiment[]; byStatus: Record<string, number>; }

const STATUS_STYLE: Record<string, string> = {
  scheduled: "text-gray-400", running: "text-yellow-600", completed: "text-green-600", aborted: "text-red-500",
};

export function ChaosSchedPanel({ experiments, byStatus }: ChaosSchedPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🐒 Chaos Scheduler</h3>
        <span className="text-xs text-gray-400">{experiments.length} experiments</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {experiments.map(e => (
          <div key={e.name} className="flex items-center justify-between px-4 py-2 text-xs">
            <div>
              <span className="font-semibold">{e.name}</span>
              <span className="text-gray-400 ml-2">{e.faultType} → {e.target} ({e.blastRadius})</span>
            </div>
            <span className={`font-bold ${STATUS_STYLE[e.status] ?? ""}`}>{e.status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
