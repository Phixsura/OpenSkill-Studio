"use client";
interface Cell { node: string; cpuPct: number; memoryPct: number; color: string; }
interface UtilHeatmapProps { cells: Cell[]; hotNodes: number; avgCpu: number; }
const COLOR_MAP: Record<string, string> = { green: "bg-green-200", yellow: "bg-yellow-200", red: "bg-red-300" };
export function UtilHeatmap({ cells, hotNodes, avgCpu }: UtilHeatmapProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🗺️ Utilization Heatmap</h3>
        <span className="text-xs text-gray-400">{hotNodes} hot · avg {avgCpu}% CPU</span>
      </div>
      <div className="flex flex-wrap gap-1 p-4">
        {cells.map(c => (
          <div key={c.node} title={`${c.node}: CPU ${c.cpuPct}% MEM ${c.memoryPct}%`}
            className={`w-8 h-8 rounded flex items-center justify-center text-[8px] ${COLOR_MAP[c.color] ?? ""}`}>
            {c.cpuPct}
          </div>
        ))}
      </div>
    </div>
  );
}
