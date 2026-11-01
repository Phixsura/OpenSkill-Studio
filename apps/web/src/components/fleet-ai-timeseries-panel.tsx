"use client";
export function FleetAiTimeseriesPanel({ models, active, forecasts, mape, horizon }: { models: number; active: number; forecasts: number; mape: number; horizon: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 AI Time Series</h3>
    <div className="text-sm">{active}/{models} active · {forecasts.toLocaleString()} forecasts · MAPE {mape}% · {horizon}d horizon</div>
  </div>);
}
