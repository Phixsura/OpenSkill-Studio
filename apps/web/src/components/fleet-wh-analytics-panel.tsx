"use client";
export function FleetWhAnalyticsPanel({ totalEvents, eventTypes, diverse }: { totalEvents: number; eventTypes: number; diverse: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔔 Webhook Analytics</h3>
    <div className="text-sm">{totalEvents.toLocaleString()} events · {eventTypes} types</div>
    {diverse && <span className="text-xs text-green-600">✅ Diverse event coverage</span>}
  </div>);
}
