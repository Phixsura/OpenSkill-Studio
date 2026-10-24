"use client";
export function FleetAiUsageFcPanel({ forecasters, active, horizon, accuracy, growth }: { forecasters: number; active: number; horizon: number; accuracy: number; growth: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 AI Usage Forecast</h3>
    <div className="text-sm">{active}/{forecasters} active · {horizon}d horizon · {accuracy}% acc · +{growth}% growth</div>
  </div>);
}
