"use client";
export function FleetPriorityPanel({ total, noPriority, allPrioritized }: { total: number; noPriority: number; allPrioritized: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⬆️ Pod Priority</h3>
    {allPrioritized ? <span className="text-xs text-green-600">✅ All {total} pods prioritized</span>
     : <span className="text-xs text-yellow-600">⚠️ {noPriority} using default priority</span>}
  </div>);
}
