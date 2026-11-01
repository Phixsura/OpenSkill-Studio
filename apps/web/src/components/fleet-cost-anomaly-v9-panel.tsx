"use client";
export function FleetCostAnomalyV9Panel({ spend, anomalies }: { spend: number; anomalies: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 Cost Anomaly v9</h3>
    <div className="text-sm">${spend.toLocaleString()} total · {anomalies} anomalies</div>
  </div>);
}
