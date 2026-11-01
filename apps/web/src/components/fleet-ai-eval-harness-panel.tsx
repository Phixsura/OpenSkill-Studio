"use client";
export function FleetAiEvalHarnessPanel({ harnesses, active, benchmarks, runs, avgScore }: { harnesses: number; active: number; benchmarks: number; runs: number; avgScore: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Eval Harness</h3>
    <div className="text-sm">{active}/{harnesses} active · {benchmarks} benchmarks · {runs.toLocaleString()} runs · {avgScore}% avg</div>
  </div>);
}
