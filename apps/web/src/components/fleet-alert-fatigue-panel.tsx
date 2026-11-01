"use client";
export function FleetAlertFatiguePanel({ total, actionable, noise, noisePct, fatiguing }: { total: number; actionable: number; noise: number; noisePct: number; fatiguing: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔔 Alert Fatigue</h3>
    <div className="text-sm">{actionable} actionable · {noise} noise ({noisePct}%)</div>
    {fatiguing && <span className="text-xs text-red-500">😴 High alert fatigue</span>}
  </div>);
}
