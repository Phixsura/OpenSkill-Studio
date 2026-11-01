"use client";
export function FleetAiAutocompletePanel({ engines, active, completions, acceptanceRate, latency }: { engines: number; active: number; completions: number; acceptanceRate: number; latency: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✨ AI Auto-Complete</h3>
    <div className="text-sm">{active}/{engines} active · {completions.toLocaleString()} completions · {acceptanceRate}% accepted · {latency}ms</div>
  </div>);
}
