"use client";
export function FleetBugBountyPanel({ totalReports, valid, totalPaid, critical }: { totalReports: number; valid: number; totalPaid: number; critical: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐛 Bug Bounty</h3>
    <div className="text-sm">{valid}/{totalReports} valid · ${totalPaid.toLocaleString()} paid · {critical} critical</div>
  </div>);
}
