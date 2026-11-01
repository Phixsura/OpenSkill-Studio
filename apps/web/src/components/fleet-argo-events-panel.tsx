"use client";
export function FleetArgoEventsPanel({ total, active, triggers, failed, reliable }: { total: number; active: number; triggers: number; failed: number; reliable: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ Argo Events</h3>
    <div className="text-sm">{active}/{total} active · {triggers.toLocaleString()} triggers/24h</div>
    {!reliable && <span className="text-xs text-red-500">⚠️ {failed} failed triggers</span>}
  </div>);
}
