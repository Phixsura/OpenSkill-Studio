"use client";
export function FleetSdkAdoptPanel({ total, outdated, upToDate }: { total: number; outdated: number; upToDate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 SDK Adoption</h3>
    <div className="text-sm">{upToDate} current · {outdated} outdated of {total}</div>
    {outdated > 0 && <span className="text-xs text-yellow-600">⚠️ {outdated} need upgrade</span>}
  </div>);
}
