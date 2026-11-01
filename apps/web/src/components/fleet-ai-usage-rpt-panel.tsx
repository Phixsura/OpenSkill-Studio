"use client";
export function FleetAiUsageRptPanel({ reporters, active, reports, recipients, insights }: { reporters: number; active: number; reports: number; recipients: number; insights: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Usage Reporter</h3>
    <div className="text-sm">{active}/{reporters} active · {reports} reports · {recipients.toLocaleString()} recipients · {insights} insights</div>
  </div>);
}
