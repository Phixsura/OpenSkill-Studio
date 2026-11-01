"use client";
export function FleetZeroTrustPanel({ total, implemented, remaining, score, mature }: { total: number; implemented: number; remaining: number; score: number; mature: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔐 Zero Trust</h3>
    <div className={`text-lg font-bold ${mature ? "text-green-600" : "text-yellow-600"}`}>{score}%</div>
    <div className="text-xs text-gray-400">{implemented}/{total} controls · {remaining} remaining</div>
  </div>);
}
