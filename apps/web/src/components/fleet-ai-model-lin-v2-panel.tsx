"use client";
export function FleetAiModelLinV2Panel({ trackers, active, models, depth, datasets }: { trackers: number; active: number; models: number; depth: number; datasets: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔗 AI Model Lineage v2</h3>
    <div className="text-sm">{active}/{trackers} active · {models} models · depth {depth} · {datasets} datasets</div>
  </div>);
}
