"use client";
export function FleetAnomalyDetPanel({ anomalies, total, mean, std }: { anomalies: number; total: number; mean: number; std: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 Anomaly Detection</h3>
    <div className="text-sm">{anomalies}/{total} anomalies · μ={mean} σ={std}</div>
    {anomalies > 0 && <span className="text-xs text-red-500">🚨 Anomalies detected</span>}
  </div>);
}
