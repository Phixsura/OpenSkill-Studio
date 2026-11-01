"use client";
export function FleetAiApiEconomyV7Panel({ trackers, active, apis, revenue, developers, calls }: { trackers: number; active: number; apis: number; revenue: number; developers: number; calls: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💼 AI API Economy v7</h3>
    <div className="text-sm">{active}/{trackers} active · {apis} APIs · ${revenue.toLocaleString()} · {developers.toLocaleString()} devs · {calls.toLocaleString()} calls</div>
  </div>);
}
