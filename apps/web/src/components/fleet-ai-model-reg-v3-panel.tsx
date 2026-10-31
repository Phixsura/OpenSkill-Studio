"use client";
export function FleetAiModelRegV3Panel({ registries, active, models, versions, deployments, tags }: { registries: number; active: number; models: number; versions: number; deployments: number; tags: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 AI Model Registry v3</h3>
    <div className="text-sm">{active}/{registries} active · {models} models · {versions} versions · {deployments} deployed · {tags} tags</div>
  </div>);
}
