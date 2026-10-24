"use client";
export function FleetMetricCardPanel({ totalSeries, sources, highCardinality, warning }: { totalSeries: number; sources: number; highCardinality: number; warning: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📏 Metric Cardinality</h3>
    <div className="text-sm">{totalSeries.toLocaleString()} series · {sources} sources</div>
    {warning && <span className="text-xs text-yellow-600">⚠️ {highCardinality} high-cardinality sources</span>}
  </div>);
}
