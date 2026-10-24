"use client";
export function FleetAiCdnPanel({ cdns, active, pops, bandwidth, cacheHit }: { cdns: number; active: number; pops: number; bandwidth: number; cacheHit: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 AI CDN</h3>
    <div className="text-sm">{active}/{cdns} active · {pops} PoPs · {bandwidth}TB bandwidth · {cacheHit}% cache hit</div>
  </div>);
}
