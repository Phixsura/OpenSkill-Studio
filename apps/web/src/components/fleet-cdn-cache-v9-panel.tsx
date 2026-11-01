"use client";
export function FleetCdnCacheV9Panel({ pops, hitRatio }: { pops: number; hitRatio: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 CDN Cache v9</h3>
    <div className="text-sm">{pops} PoPs · {(hitRatio * 100).toFixed(0)}% hit ratio</div>
  </div>);
}
