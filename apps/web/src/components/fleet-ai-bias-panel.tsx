"use client";
export function FleetAiBiasPanel({ monitors, active, modelsAudited, biasAlerts, fair }: { monitors: number; active: number; modelsAudited: number; biasAlerts: number; fair: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚖️ AI Bias Detection</h3>
    <div className="text-sm">{active}/{monitors} active · {modelsAudited} audited</div>
    {fair ? <span className="text-xs text-green-600">✅ Fair</span> : <span className="text-xs text-red-500">⚠️ {biasAlerts} bias alerts</span>}
  </div>);
}
