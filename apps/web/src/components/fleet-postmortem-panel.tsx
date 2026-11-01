"use client";
export function FleetPostmortemPanel({ total, postmortemsDone, actionsCompleted, completionPct }: { total: number; postmortemsDone: number; actionsCompleted: number; completionPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📝 Postmortems</h3>
    <div className="text-sm">{postmortemsDone}/{total} done ({completionPct}%) · {actionsCompleted} actions closed</div>
  </div>);
}
