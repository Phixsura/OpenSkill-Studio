"use client";
export function FleetAiAlertMgrPanel({ managers, active, alerts, acked, silenced, channels }: { managers: number; active: number; alerts: number; acked: number; silenced: number; channels: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚨 AI Alert Manager</h3>
    <div className="text-sm">{active}/{managers} active · {alerts} alerts · {acked} acked · {silenced} silenced · {channels} channels</div>
  </div>);
}
