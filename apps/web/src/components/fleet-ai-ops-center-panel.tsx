"use client";
export function FleetAiOpsCenterPanel({ centers, active, operators, alerts, actions, regions }: { centers: number; active: number; operators: number; alerts: number; actions: number; regions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏢 AI Ops Center</h3>
    <div className="text-sm">{active}/{centers} active · {operators} operators · {alerts} alerts · {actions} actions · {regions} regions</div>
  </div>);
}
