"use client";
export function FleetAuditLogPanel({ totalEvents, types }: { totalEvents: number; types: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 Audit Log</h3>
    <div className="text-sm">{totalEvents.toLocaleString()} events · {types} types</div>
  </div>);
}
