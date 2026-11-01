"use client";
export function FleetCustomMetricV9Panel({ metrics, dpm }: { metrics: number; dpm: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📏 Custom Metrics v9</h3>
    <div className="text-sm">{metrics} metrics · {dpm.toLocaleString()} dpm</div>
  </div>);
}
