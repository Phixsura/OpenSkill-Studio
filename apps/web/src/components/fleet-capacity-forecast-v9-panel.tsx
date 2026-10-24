"use client";
export function FleetCapacityForecastV9Panel({ resources, atRisk }: { resources: number; atRisk: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📉 Capacity Forecast v9</h3>
    <div className="text-sm">{resources} resources · {atRisk} at risk</div>
  </div>);
}
