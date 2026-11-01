"use client";
export function FleetAiInfCachePanel({ caches, active, entries, hitRate, costSaved }: { caches: number; active: number; entries: number; hitRate: number; costSaved: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 AI Inference Cache</h3>
    <div className="text-sm">{active}/{caches} active · {entries.toLocaleString()} entries · {hitRate}% hit · ${costSaved.toLocaleString()} saved</div>
  </div>);
}
