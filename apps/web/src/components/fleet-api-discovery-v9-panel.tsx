"use client";
export function FleetApiDiscoveryV9Panel({ sources, discovered }: { sources: number; discovered: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 API Discovery v9</h3>
    <div className="text-sm">{sources} sources · {discovered} discovered</div>
  </div>);
}
