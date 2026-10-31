"use client";
export function FleetCloudfrontPanel({ distributions, deployed, requests, cacheHit }: { distributions: number; deployed: number; requests: number; cacheHit: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 CloudFront</h3>
    <div className="text-sm">{deployed}/{distributions} deployed · {requests.toLocaleString()} req · {cacheHit}% hit</div>
  </div>);
}
