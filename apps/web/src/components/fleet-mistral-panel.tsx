"use client";
export function FleetMistralPanel({ deployments, active, completions, tokens }: { deployments: number; active: number; completions: number; tokens: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌪️ Mistral</h3>
    <div className="text-sm">{active}/{deployments} active · {completions.toLocaleString()} completions · {tokens.toLocaleString()} tokens</div>
  </div>);
}
