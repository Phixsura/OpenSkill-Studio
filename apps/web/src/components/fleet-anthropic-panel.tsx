"use client";
export function FleetAnthropicPanel({ projects, active, requests, tokens }: { projects: number; active: number; requests: number; tokens: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤖 Anthropic</h3>
    <div className="text-sm">{active}/{projects} active · {requests.toLocaleString()} req · {tokens.toLocaleString()} tokens</div>
  </div>);
}
