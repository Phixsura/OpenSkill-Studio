"use client";
export function FleetAiStartupPrbPanel({ probes, active, services, startup, failures }: { probes: number; active: number; services: number; startup: number; failures: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 AI Startup Probe</h3>
    <div className="text-sm">{active}/{probes} active · {services} services · {startup}s startup · {failures} failures</div>
  </div>);
}
