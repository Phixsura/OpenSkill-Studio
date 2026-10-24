"use client";
export function FleetAiForecastPanel({ models, active, predictions, mape }: { models: number; active: number; predictions: number; mape: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 AI Forecasting</h3>
    <div className="text-sm">{active}/{models} active · {predictions.toLocaleString()} predictions · {mape}% MAPE</div>
  </div>);
}
