"use client";
export function FleetChaosReportV9Panel({ reports, improvements }: { reports: number; improvements: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 Chaos Report v9</h3>
    <div className="text-sm">{reports} reports · {improvements} improvements</div>
  </div>);
}
