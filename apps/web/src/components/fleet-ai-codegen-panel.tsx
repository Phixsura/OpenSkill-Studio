"use client";
export function FleetAiCodegenPanel({ services, active, completions, acceptanceRate, linesGenerated }: { services: number; active: number; completions: number; acceptanceRate: number; linesGenerated: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💻 AI Code Gen</h3>
    <div className="text-sm">{active}/{services} active · {completions.toLocaleString()} completions · {acceptanceRate}% accepted</div>
  </div>);
}
