"use client";
export function FleetSlaReportPanel({ month, uptimePct, targetPct, met, credits }: { month: string; uptimePct: number; targetPct: number; met: boolean; credits: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 SLA Report — {month}</h3>
    <div className={`text-lg font-bold ${met ? "text-green-600" : "text-red-500"}`}>{uptimePct}% / {targetPct}%</div>
    {!met && <span className="text-xs text-red-500">💸 ${credits} credits owed</span>}
  </div>);
}
