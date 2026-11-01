"use client";
export function FleetAiModelRegPanel({ registries, active, models, versions, deployed, coverage }: { registries: number; active: number; models: number; versions: number; deployed: number; coverage: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 AI Model Registry</h3>
    <div className="text-sm">{active}/{registries} active · {models} models · {versions} versions · {deployed} deployed ({coverage}%)</div>
  </div>);
}
