"use client";
export function FleetAiCacheLayerPanel({ caches, active, hitRate, entries, savedTokens }: { caches: number; active: number; hitRate: number; entries: number; savedTokens: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💾 AI Cache Layer</h3>
    <div className="text-sm">{active}/{caches} active · {hitRate}% hit · {entries.toLocaleString()} entries · {savedTokens.toLocaleString()} tokens saved</div>
  </div>);
}
