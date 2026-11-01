"use client";
export function FleetAiBenchPanel({ benches, active, models, suites, runs }: { benches: number; active: number; models: number; suites: number; runs: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📏 AI Benchmark</h3>
    <div className="text-sm">{active}/{benches} active · {models} models · {suites} suites · {runs.toLocaleString()} runs</div>
  </div>);
}
