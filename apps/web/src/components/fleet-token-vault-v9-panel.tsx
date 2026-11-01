"use client";
export function FleetTokenVaultV9Panel({ tokens, calls }: { tokens: number; calls: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔑 Token Vault v9</h3>
    <div className="text-sm">{tokens} tokens · {calls.toLocaleString()} calls/day</div>
  </div>);
}
