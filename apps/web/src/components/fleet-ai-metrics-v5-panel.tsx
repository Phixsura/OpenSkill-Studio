"use client";
export function FleetAiMetricsV5Panel({ collectors, active, metrics, series, cardinality, resolution }: { collectors: number; active: number; metrics: number; series: number; cardinality: number; resolution: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Metrics v5</h3>
    <div className="text-sm">{active}/{collectors} active · {metrics.toLocaleString()} metrics · {series.toLocaleString()} series · {resolution}s resolution</div>
  </div>);
}
