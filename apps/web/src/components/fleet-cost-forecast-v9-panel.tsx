"use client";
export function FleetCostForecastV9Panel({ forecasts, accurate }: { forecasts: number; accurate: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📉 Cost Forecast v9</h3>
    <div className="text-sm">{forecasts} forecasts · {accurate} accurate</div>
  </div>);
}
