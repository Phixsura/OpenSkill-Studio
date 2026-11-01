"use client";
export function FleetIncCommPanel({ total, notified, notNotified, avgNotifyMin, timely }: { total: number; notified: number; notNotified: number; avgNotifyMin: number; timely: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📢 Incident Comms</h3>
    <div className="text-sm">{notified}/{total} notified · avg {avgNotifyMin}min</div>
    {notNotified > 0 && <span className="text-xs text-yellow-600">⚠️ {notNotified} not communicated</span>}
  </div>);
}
