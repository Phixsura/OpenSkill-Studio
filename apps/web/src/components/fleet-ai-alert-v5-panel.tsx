"use client";
export function FleetAiAlertV5Panel({ systems, active, alerts, acked, autoResolved, noiseReduction }: { systems: number; active: number; alerts: number; acked: number; autoResolved: number; noiseReduction: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚨 AI Alerting v5</h3>
    <div className="text-sm">{active}/{systems} active · {alerts} alerts · {acked} acked · {autoResolved} auto · {noiseReduction}% noise↓</div>
  </div>);
}
