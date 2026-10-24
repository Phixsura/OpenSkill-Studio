"use client";
export function FleetAiAnomalyPanel({ detectors, active, anomalies, dataPoints }: { detectors: number; active: number; anomalies: number; dataPoints: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 AI Anomaly Detection</h3>
    <div className="text-sm">{active}/{detectors} active · {anomalies} anomalies · {dataPoints.toLocaleString()} data points</div>
  </div>);
}
