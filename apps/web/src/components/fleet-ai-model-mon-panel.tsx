"use client";
export function FleetAiModelMonPanel({ monitors, active, models, driftAlerts, perfAlerts, stable }: { monitors: number; active: number; models: number; driftAlerts: number; perfAlerts: number; stable: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Model Monitoring</h3>
    <div className="text-sm">{active}/{monitors} active · {models} models</div>
    {stable ? <span className="text-xs text-green-600">✅ Stable</span>
     : <span className="text-xs text-yellow-600">⚠️ {driftAlerts} drift · {perfAlerts} perf alerts</span>}
  </div>);
}
