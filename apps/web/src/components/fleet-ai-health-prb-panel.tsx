"use client";
export function FleetAiHealthPrbPanel({ probes, active, endpoints, checks, deps, allHealthy }: { probes: number; active: number; endpoints: number; checks: number; deps: number; allHealthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💚 AI Health Probe v2</h3>
    <div className="text-sm">{active}/{probes} active · {endpoints} endpoints · {checks.toLocaleString()} checks · {deps} deps · {allHealthy ? "✅" : "⚠️"}</div>
  </div>);
}
