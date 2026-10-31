"use client";
export function FleetAiReportV5Panel({ reporters, active, reports, recipients, templates }: { reporters: number; active: number; reports: number; recipients: number; templates: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Reporting v5</h3>
    <div className="text-sm">{active}/{reporters} active · {reports} reports · {recipients.toLocaleString()} recipients · {templates} templates</div>
  </div>);
}
