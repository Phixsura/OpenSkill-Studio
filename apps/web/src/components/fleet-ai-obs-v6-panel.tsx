"use client";
export function FleetAiObsV6Panel({ stacks, active, pillars, dashboards, alerts }: { stacks: number; active: number; pillars: number; dashboards: number; alerts: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 AI Observability v6</h3>
    <div className="text-sm">{active}/{stacks} active · {pillars}/{stacks} 3-pillar · {dashboards} dashboards · {alerts} alerts</div>
  </div>);
}
