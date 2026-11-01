"use client";
export function FleetSupportPanel({ total, open, resolved, avgResolution, backlogHealthy }: { total: number; open: number; resolved: number; avgResolution: number; backlogHealthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎫 Support Tickets</h3>
    <div className="text-sm">{open} open · {resolved} resolved · avg {avgResolution}h</div>
    {!backlogHealthy && <span className="text-xs text-red-500">⚠️ Large backlog</span>}
  </div>);
}
