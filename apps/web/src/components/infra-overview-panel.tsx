"use client";

interface InfraOverviewPanelProps { displayCost: string; health: string;
  nodes: number; cpuCores: number; memoryGb: number; storageTb: number; bandwidthGbps: number; }

export function InfraOverviewPanel({ displayCost, health, nodes, cpuCores, memoryGb, storageTb, bandwidthGbps }: InfraOverviewPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏗️ Infrastructure</h3>
        <div className="flex gap-2 text-xs">
          <span className="font-bold">{displayCost}</span>
          <span className={health === "healthy" ? "text-green-600" : "text-yellow-600"}>{health}</span>
        </div>
      </div>
      <div className="grid grid-cols-5 gap-px bg-gray-200 dark:bg-gray-700">
        {[{ l: "Nodes", v: nodes }, { l: "CPU", v: `${cpuCores} cores` },
          { l: "RAM", v: `${memoryGb} GB` }, { l: "Storage", v: `${storageTb} TB` },
          { l: "Network", v: `${bandwidthGbps} Gbps` }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-2 text-center">
            <div className="text-sm font-bold">{s.v}</div>
            <div className="text-[9px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
