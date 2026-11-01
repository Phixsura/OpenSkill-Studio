"use client";
interface ClusterOptPanelProps { cpuUtilPct: number; memUtilPct: number; recommendation: string;
  nodes: number; pods: number; totalCpu: number; totalMemGb: number; }
const REC_STYLE: Record<string, string> = { optimal: "text-green-600", scale_up: "text-red-500", scale_down: "text-blue-500" };
export function ClusterOptPanel({ cpuUtilPct, memUtilPct, recommendation, nodes, pods, totalCpu, totalMemGb }: ClusterOptPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚙️ Cluster Optimizer</h3>
        <span className={`text-xs font-bold ${REC_STYLE[recommendation] ?? ""}`}>
          {recommendation.replace("_", " ")} · {nodes} nodes · {pods} pods
        </span>
      </div>
      <div className="grid grid-cols-2 gap-3 p-4">
        <div><div className="flex justify-between text-xs mb-0.5"><span className="text-gray-400">CPU</span><span>{cpuUtilPct}%</span></div>
          <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
            <div className={`h-full rounded-full ${cpuUtilPct > 80 ? "bg-red-500" : cpuUtilPct < 30 ? "bg-blue-400" : "bg-green-500"}`}
              style={{ width: `${cpuUtilPct}%` }} /></div></div>
        <div><div className="flex justify-between text-xs mb-0.5"><span className="text-gray-400">Memory</span><span>{memUtilPct}%</span></div>
          <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
            <div className={`h-full rounded-full ${memUtilPct > 80 ? "bg-red-500" : memUtilPct < 30 ? "bg-blue-400" : "bg-green-500"}`}
              style={{ width: `${memUtilPct}%` }} /></div></div>
      </div>
    </div>
  );
}
