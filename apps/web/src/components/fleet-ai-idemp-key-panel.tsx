"use client";
export function FleetAiIdempKeyPanel({ managers, active, keys, prevented, ttl }: { managers: number; active: number; keys: number; prevented: number; ttl: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔑 AI Idempotency</h3>
    <div className="text-sm">{active}/{managers} active · {keys.toLocaleString()} keys · {prevented.toLocaleString()} prevented · TTL {ttl}s</div>
  </div>);
}
