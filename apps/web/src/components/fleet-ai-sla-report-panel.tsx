"use client";
export function FleetAiSlaReportPanel({ reporters, active, reports, slos, compliance }: { reporters: number; active: number; reports: number; slos: number; compliance: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI SLA Reporter</h3>
    <div className="text-sm">{active}/{reporters} active · {reports} reports · {slos} SLOs · {compliance}% compliant</div>
  </div>);
}
