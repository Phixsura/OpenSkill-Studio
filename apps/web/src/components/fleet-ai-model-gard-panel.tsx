"use client";
export function FleetAiModelGardPanel({ gardens, active, models, categories, downloads }: { gardens: number; active: number; models: number; categories: number; downloads: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌿 AI Model Garden</h3>
    <div className="text-sm">{active}/{gardens} active · {models} models · {categories} categories · {downloads.toLocaleString()} downloads</div>
  </div>);
}
