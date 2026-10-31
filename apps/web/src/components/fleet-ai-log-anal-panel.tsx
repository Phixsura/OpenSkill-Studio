"use client";
export function FleetAiLogAnalPanel({ analyzers, active, logs, patterns, insights }: { analyzers: number; active: number; logs: number; patterns: number; insights: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📝 AI Log Analysis</h3>
    <div className="text-sm">{active}/{analyzers} active · {logs.toLocaleString()} logs · {patterns} patterns · {insights} insights</div>
  </div>);
}
