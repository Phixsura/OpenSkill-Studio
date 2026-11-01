"use client";
export function FleetAiExecReportV7Panel({ reporters, active, reports, stakeholders, kpis }: { reporters: number; active: number; reports: number; stakeholders: number; kpis: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👔 AI Executive Report v7</h3>
    <div className="text-sm">{active}/{reporters} active · {reports} reports · {stakeholders} stakeholders · {kpis} KPIs</div>
  </div>);
}
