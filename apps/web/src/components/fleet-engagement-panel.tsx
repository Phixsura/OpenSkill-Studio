"use client";
export function FleetEngagementPanel({ dau, mau, stickinessPct, avgSessionMin, engaged }: { dau: number; mau: number; stickinessPct: number; avgSessionMin: number; engaged: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👥 Engagement</h3>
    <div className="text-sm">{dau.toLocaleString()} DAU / {mau.toLocaleString()} MAU · {stickinessPct}% sticky</div>
    <div className="text-xs text-gray-400">avg {avgSessionMin}min/session</div>
  </div>);
}
