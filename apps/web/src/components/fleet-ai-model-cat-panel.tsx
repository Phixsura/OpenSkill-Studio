"use client";
export function FleetAiModelCatPanel({ catalogs, active, models, providers, deployments }: { catalogs: number; active: number; models: number; providers: number; deployments: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📚 AI Model Catalog</h3>
    <div className="text-sm">{active}/{catalogs} active · {models} models · {providers} providers · {deployments} deployments</div>
  </div>);
}
