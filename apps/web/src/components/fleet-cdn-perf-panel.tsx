"use client";
export function FleetCdnPerfPanel({ hitRate, avgLatency, pops, effective }: { hitRate: number; avgLatency: number; pops: number; effective: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 CDN Performance</h3>
    <div className="text-sm">{hitRate}% hit rate · {avgLatency}ms · {pops} PoPs</div>
    <span className={`text-xs ${effective ? "text-green-600" : "text-yellow-600"}`}>{effective ? "✅ Effective" : "⚠️ Low hit rate"}</span>
  </div>);
}
