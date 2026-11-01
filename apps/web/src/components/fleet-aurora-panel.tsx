"use client";
export function FleetAuroraPanel({ clusters, available, serverless, currentAcu }: { clusters: number; available: number; serverless: number; currentAcu: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌌 Aurora</h3>
    <div className="text-sm">{available}/{clusters} available · {serverless} serverless · {currentAcu} ACU</div>
  </div>);
}
