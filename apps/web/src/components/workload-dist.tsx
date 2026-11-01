"use client";

interface WorkloadDistProps { nodes: number; avgLoad: number; spread: number;
  maxLoad: number; minLoad: number; balanced: boolean; hotspot: string | null; }

export function WorkloadDist({ nodes, avgLoad, spread, maxLoad, minLoad, balanced, hotspot }: WorkloadDistProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚖️ Workload Distribution</h3>
        <span className={`text-xs ${balanced ? "text-green-600" : "text-yellow-600"}`}>
          {balanced ? "✅ Balanced" : `⚠ Imbalanced${hotspot ? ` — hotspot: ${hotspot}` : ""}`}
        </span>
      </div>
      <div className="grid grid-cols-5 gap-px bg-gray-200 dark:bg-gray-700">
        {[{ l: "Nodes", v: nodes }, { l: "Avg", v: `${avgLoad}%` },
          { l: "Min", v: `${minLoad}%` }, { l: "Max", v: `${maxLoad}%` },
          { l: "Spread", v: `${spread}%` }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-2 text-center">
            <div className="text-sm font-bold">{s.v}</div>
            <div className="text-[9px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
