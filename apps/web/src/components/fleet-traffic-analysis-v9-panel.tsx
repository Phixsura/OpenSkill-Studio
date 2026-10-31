"use client";
export function FleetTrafficAnalysisV9Panel({ apis, anomalous }: { apis: number; anomalous: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Traffic Analysis v9</h3>
    <div className="text-sm">{apis} APIs · {anomalous} anomalous</div>
  </div>);
}
