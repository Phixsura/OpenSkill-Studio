"use client";
export function FleetAiModelVerPanel({ registries, models, versions, active }: { registries: number; models: number; versions: number; active: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 Model Versioning</h3>
    <div className="text-sm">{registries} registries · {models} models · {versions} versions · {active} active</div>
  </div>);
}
