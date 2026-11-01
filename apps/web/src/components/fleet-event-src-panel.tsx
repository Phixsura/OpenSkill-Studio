"use client";
export function FleetEventSrcPanel({ stores, totalEvents, snapshots, avgReplay, fast }: { stores: number; totalEvents: number; snapshots: number; avgReplay: number; fast: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📜 Event Sourcing</h3>
    <div className="text-sm">{totalEvents.toLocaleString()} events · {snapshots} snapshots · {avgReplay}ms replay</div>
    {!fast && <span className="text-xs text-yellow-600">⚠️ Slow replay</span>}
  </div>);
}
