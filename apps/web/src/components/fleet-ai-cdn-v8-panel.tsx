"use client";
export function FleetAiCdnV8Panel({ cdns, active, pops, pbps, hitPct }: { cdns: number; active: number; pops: number; pbps: number; hitPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 AI CDN v8</h3>
    <div className="text-sm">{active}/{cdns} active · {pops} PoPs · {pbps}Pbps · {hitPct}% cache hit</div>
  </div>);
}
