"use client";
export function FleetAiCachePanel({ caches, active, hitRate, tokensSaved, costSaved }: { caches: number; active: number; hitRate: number; tokensSaved: number; costSaved: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ AI Cache</h3>
    <div className="text-sm">{active}/{caches} active · {hitRate}% hit · {tokensSaved.toLocaleString()} tokens · ${costSaved} saved</div>
  </div>);
}
