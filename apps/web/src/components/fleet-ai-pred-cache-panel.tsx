"use client";
export function FleetAiPredCachePanel({ caches, active, entries, hitRate, savedMs }: { caches: number; active: number; entries: number; hitRate: number; savedMs: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💾 AI Prediction Cache</h3>
    <div className="text-sm">{active}/{caches} active · {entries.toLocaleString()} entries · {hitRate}% hit · {savedMs}ms saved</div>
  </div>);
}
