"use client";
export function FleetAiCodegenPanel({ engines, active, completions, acceptanceRate, languages }: { engines: number; active: number; completions: number; acceptanceRate: number; languages: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💻 AI Code Generation</h3>
    <div className="text-sm">{active}/{engines} active · {completions.toLocaleString()} completions · {acceptanceRate}% accepted · {languages} langs</div>
  </div>);
}
