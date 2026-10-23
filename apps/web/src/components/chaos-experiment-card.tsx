"use client";

interface ChaosExperiment { id: string; name: string; target: string;
  faultType: string; status: string; blastRadiusPct: number; }
interface ChaosExperimentCardProps { experiments: ChaosExperiment[];
  onStart: (id: string) => void; }

const FAULT_ICON: Record<string, string> = {
  pod_kill: "💀", latency: "🐌", cpu_stress: "🔥", network_partition: "🔌", disk_fill: "💾",
};
const STATUS_BADGE: Record<string, string> = {
  created: "bg-gray-100 text-gray-600", running: "bg-yellow-100 text-yellow-700",
  completed: "bg-green-100 text-green-700",
};

export function ChaosExperimentCard({ experiments, onStart }: ChaosExperimentCardProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🌪️ Chaos Experiments</h3>
      <div className="space-y-2">
        {experiments.map(e => (
          <div key={e.id} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-4 py-3">
            <div>
              <div className="flex items-center gap-2">
                <span>{FAULT_ICON[e.faultType] || "⚡"}</span>
                <span className="text-sm font-medium">{e.name}</span>
                <span className={`text-xs px-1.5 py-0.5 rounded ${STATUS_BADGE[e.status] || ""}`}>{e.status}</span>
              </div>
              <p className="text-xs text-gray-400 mt-0.5">Target: {e.target} · {e.blastRadiusPct}% blast radius</p>
            </div>
            {e.status === "created" && (
              <button onClick={() => onStart(e.id)}
                className="text-xs px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700">Run</button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
