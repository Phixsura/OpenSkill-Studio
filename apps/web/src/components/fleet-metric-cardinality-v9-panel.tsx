"use client";
export function FleetMetricCardinalityV9Panel({ metrics, highCard }: { metrics: number; highCard: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Metric Cardinality v9</h3>
    <div className="text-sm">{metrics} metrics · {highCard} high cardinality</div>
  </div>);
}
