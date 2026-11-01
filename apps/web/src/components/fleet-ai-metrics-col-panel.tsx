"use client";
export function FleetAiMetricsColPanel({ collectors, active, metrics, series, resolution }: { collectors: number; active: number; metrics: number; series: number; resolution: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Metrics Collector</h3>
    <div className="text-sm">{active}/{collectors} active · {metrics.toLocaleString()} metrics · {series.toLocaleString()} series · {resolution}s res</div>
  </div>);
}
