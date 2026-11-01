"use client";
export function FleetGrowthRatePanel({ avgRate, latestRate, accelerating }: { avgRate: number; latestRate: number; accelerating: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 Growth Rate</h3>
    <div className="text-sm">avg +{avgRate}/period · latest +{latestRate}</div>
    {accelerating && <span className="text-xs text-green-600">🚀 Accelerating!</span>}
  </div>);
}
