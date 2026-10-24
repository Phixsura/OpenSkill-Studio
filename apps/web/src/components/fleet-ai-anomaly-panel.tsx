"use client";
export function FleetAiAnomalyPanel({ detectors, active, metrics, anomalies, fpRate }: { detectors: number; active: number; metrics: number; anomalies: number; fpRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔮 AI Anomaly Detection</h3>
    <div className="text-sm">{active}/{detectors} active · {metrics.toLocaleString()} metrics · {anomalies} anomalies · {fpRate}% FP</div>
  </div>);
}
