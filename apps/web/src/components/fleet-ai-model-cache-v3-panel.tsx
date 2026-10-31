"use client";
export function FleetAiModelCacheV3Panel({ caches, active, models, hitRate, memory }: { caches: number; active: number; models: number; hitRate: number; memory: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💾 AI Model Cache v3</h3>
    <div className="text-sm">{active}/{caches} active · {models} models · {hitRate}% hit · {memory}GB</div>
  </div>);
}
