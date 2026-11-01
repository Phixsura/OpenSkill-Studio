"use client";
export function FleetInnovationPanel({ newFeatures, experiments, adoptionRate, index, innovative }: { newFeatures: number; experiments: number; adoptionRate: number; index: number; innovative: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💡 Innovation Index</h3>
    <div className={`text-lg font-bold ${innovative ? "text-green-600" : "text-yellow-600"}`}>{index}</div>
    <div className="text-xs text-gray-400">{newFeatures} features · {experiments} experiments · {adoptionRate}% adoption</div>
  </div>);
}
