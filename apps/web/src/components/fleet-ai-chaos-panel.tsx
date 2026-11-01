"use client";
export function FleetAiChaosPanel({ experiments, active, runs, failures, systems }: { experiments: number; active: number; runs: number; failures: number; systems: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌪️ AI Chaos Engineering</h3>
    <div className="text-sm">{active}/{experiments} active · {runs} runs · {failures} failures found · {systems} systems</div>
  </div>);
}
