"use client";
export function FleetWeightsPanel({ registries, active, models, versions, storageTb }: { registries: number; active: number; models: number; versions: number; storageTb: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚖️ Model Weights</h3>
    <div className="text-sm">{active}/{registries} active · {models} models · {versions} versions · {storageTb}TB</div>
  </div>);
}
