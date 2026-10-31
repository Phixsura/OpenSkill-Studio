"use client";
export function FleetAiBoardReportV7Panel({ reports, active, quarterly, metrics, revenue }: { reports: number; active: number; quarterly: number; metrics: number; revenue: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Board Report v7</h3>
    <div className="text-sm">{active}/{reports} active · {quarterly} quarterly · {metrics} metrics · ${revenue.toLocaleString()} impact</div>
  </div>);
}
