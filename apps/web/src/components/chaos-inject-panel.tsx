"use client";

interface Experiment { type: string; service?: string; active?: boolean; triggered?: boolean; addedMs?: number; }
interface ChaosInjectPanelProps { experiments: Experiment[]; activeCount: number; }

const TYPE_ICON: Record<string, string> = {
  latency: "⏱️", error: "💥", network_partition: "🔌",
};

export function ChaosInjectPanel({ experiments, activeCount }: ChaosInjectPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🐒 Chaos Engineering</h3>
        <span className={`text-xs ${activeCount > 0 ? "text-red-500" : "text-green-600"}`}>
          {activeCount} active / {experiments.length} total
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {experiments.map((e, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span>{TYPE_ICON[e.type] ?? "🔧"}</span>
              <span className="font-mono">{e.type}</span>
              {e.service && <span className="text-gray-400">{e.service}</span>}
            </div>
            <span className={e.active || e.triggered ? "text-red-500" : "text-gray-400"}>
              {e.active || e.triggered ? "ACTIVE" : "inactive"}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
