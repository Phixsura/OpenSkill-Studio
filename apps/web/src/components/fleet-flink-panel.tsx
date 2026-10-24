"use client";
export function FleetFlinkPanel({ clusters, running, taskSlots, checkpointsOk }: { clusters: number; running: number; taskSlots: number; checkpointsOk: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 Flink</h3>
    <div className="text-sm">{running}/{clusters} running · {taskSlots} slots</div>
    {!checkpointsOk && <span className="text-xs text-red-500">⚠️ Checkpoint issues</span>}
  </div>);
}
