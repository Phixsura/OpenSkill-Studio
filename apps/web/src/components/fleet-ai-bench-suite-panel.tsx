"use client";
export function FleetAiBenchSuitePanel({ suites, active, benchmarks, models, runs }: { suites: number; active: number; benchmarks: number; models: number; runs: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📏 AI Benchmark Suite</h3>
    <div className="text-sm">{active}/{suites} active · {benchmarks} benchmarks · {models} models · {runs.toLocaleString()} runs</div>
  </div>);
}
