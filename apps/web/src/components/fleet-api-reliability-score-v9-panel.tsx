"use client";
export function FleetApiReliabilityScoreV9Panel({ services, score }: { services: number; score: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💎 Reliability Score v9</h3>
    <div className="text-sm">{services} services · {score}% reliability</div>
  </div>);
}
