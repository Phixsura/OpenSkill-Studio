"use client";
export function FleetAiPlatStatusV2Panel({ pages, active, components, operational, incidents, uptime, status }: { pages: number; active: number; components: number; operational: number; incidents: number; uptime: number; status: string; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 AI Status Page v2</h3>
    <div className="text-sm">{active}/{pages} active · {operational}/{components} operational · {incidents} incidents · {uptime}%</div>
    <div className="text-xs mt-1 font-bold">{status}</div>
  </div>);
}
