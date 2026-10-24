"use client";
export function FleetAiModelMonPanel({ monitors, active, models, alerts, degraded }: { monitors: number; active: number; models: number; alerts: number; degraded: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 AI Model Monitor</h3>
    <div className="text-sm">{active}/{monitors} active · {models} models · {alerts} alerts · {degraded} degraded</div>
  </div>);
}
