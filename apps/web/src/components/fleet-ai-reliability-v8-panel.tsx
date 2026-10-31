"use client";
export function FleetAiReliabilityV8Panel({ systems, active, uptime, mttr, budget }: { systems: number; active: number; uptime: number; mttr: number; budget: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ AI Reliability v8</h3>
    <div className="text-sm">{active}/{systems} active · {uptime}% uptime · MTTR {mttr}m · {budget}% budget</div>
  </div>);
}
