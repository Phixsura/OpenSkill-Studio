"use client";
export function FleetAiReadyGatePanel({ gates, active, services, ready, checks }: { gates: number; active: number; services: number; ready: number; checks: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✅ AI Readiness Gate</h3>
    <div className="text-sm">{active}/{gates} active · {ready}/{services} ready · {checks} checks</div>
  </div>);
}
