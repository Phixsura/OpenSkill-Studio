"use client";
export function FleetOpenaiPanel({ orgs, active, requests, cost }: { orgs: number; active: number; requests: number; cost: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤖 OpenAI</h3>
    <div className="text-sm">{active}/{orgs} active · {requests.toLocaleString()} req · ${cost.toLocaleString()}/24h</div>
  </div>);
}
