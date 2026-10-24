"use client";
export function FleetAiApiKeyPanel({ managers, active, keys, revoked, requests }: { managers: number; active: number; keys: number; revoked: number; requests: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔑 AI API Keys</h3>
    <div className="text-sm">{active}/{managers} active · {keys.toLocaleString()} keys · {revoked} revoked · {requests.toLocaleString()} req</div>
  </div>);
}
