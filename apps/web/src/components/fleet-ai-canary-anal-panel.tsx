"use client";
export function FleetAiCanaryAnalPanel({ analyzers, active, analyses, promoted, rolledBack }: { analyzers: number; active: number; analyses: number; promoted: number; rolledBack: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐤 AI Canary Analysis</h3>
    <div className="text-sm">{active}/{analyzers} active · {analyses} analyses · {promoted} promoted · {rolledBack} rolled back</div>
  </div>);
}
