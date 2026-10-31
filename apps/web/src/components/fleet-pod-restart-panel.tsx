"use client";
export function FleetPodRestartPanel({ totalRestarts, crashlooping, pods, stable }: { totalRestarts: number; crashlooping: number; pods: number; stable: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 Pod Restarts</h3>
    <div className="text-sm">{totalRestarts} restarts across {pods} pods</div>
    {!stable && <span className="text-xs text-red-500">⚠️ {crashlooping} crashlooping</span>}
  </div>);
}
