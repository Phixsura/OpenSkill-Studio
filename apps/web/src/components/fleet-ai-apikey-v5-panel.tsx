"use client";
export function FleetAiApikeyV5Panel({ managers, active, keys, created, revoked }: { managers: number; active: number; keys: number; created: number; revoked: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔑 AI API Key v5</h3>
    <div className="text-sm">{active}/{managers} active · {keys.toLocaleString()} keys · {created} created · {revoked} revoked</div>
  </div>);
}
