"use client";
export function FleetCodecovPanel({ total, withCodecov, avgCoverage, declining }: { total: number; withCodecov: number; avgCoverage: number; declining: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☂️ Codecov</h3>
    <div className="text-sm">{withCodecov}/{total} reporting · {avgCoverage}% avg</div>
    {declining > 0 && <span className="text-xs text-yellow-600">📉 {declining} declining</span>}
  </div>);
}
