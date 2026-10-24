"use client";
export function FleetAiBiasDetPanel({ detectors, active, scans, alerts, fairness }: { detectors: number; active: number; scans: number; alerts: number; fairness: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚖️ AI Bias Detection</h3>
    <div className="text-sm">{active}/{detectors} active · {scans.toLocaleString()} scans · {alerts} alerts · fairness {fairness}</div>
  </div>);
}
