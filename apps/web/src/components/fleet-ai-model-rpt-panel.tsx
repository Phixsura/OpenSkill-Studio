"use client";
export function FleetAiModelRptPanel({ reporters, active, reports, metrics, stakeholders }: { reporters: number; active: number; reports: number; metrics: number; stakeholders: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Model Report</h3>
    <div className="text-sm">{active}/{reporters} active · {reports} reports · {metrics} metrics · {stakeholders} stakeholders</div>
  </div>);
}
