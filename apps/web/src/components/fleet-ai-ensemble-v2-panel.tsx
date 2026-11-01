"use client";
export function FleetAiEnsembleV2Panel({ ensembles, active, avgModels, requests, boost }: { ensembles: number; active: number; avgModels: number; requests: number; boost: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔀 AI Ensemble v2</h3>
    <div className="text-sm">{active}/{ensembles} active · {avgModels} models/ensemble · {requests.toLocaleString()} req · +{boost}% boost</div>
  </div>);
}
