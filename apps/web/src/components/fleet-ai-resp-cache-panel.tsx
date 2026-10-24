"use client";
export function FleetAiRespCachePanel({ caches, active, entries, hitRate, tokensSaved }: { caches: number; active: number; entries: number; hitRate: number; tokensSaved: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💾 AI Response Cache v2</h3>
    <div className="text-sm">{active}/{caches} active · {entries.toLocaleString()} entries · {hitRate}% hit · {tokensSaved.toLocaleString()} tokens saved</div>
  </div>);
}
