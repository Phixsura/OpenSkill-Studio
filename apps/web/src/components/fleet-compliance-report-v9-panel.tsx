"use client";
export function FleetComplianceReportV9Panel({ reports, findings }: { reports: number; findings: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✅ Compliance Report v9</h3>
    <div className="text-sm">{reports} reports · {findings} findings</div>
  </div>);
}
