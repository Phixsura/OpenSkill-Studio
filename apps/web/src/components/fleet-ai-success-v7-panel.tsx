"use client";
export function FleetAiSuccessV7Panel({ trackers, active, health, churnRisk, expansion }: { trackers: number; active: number; health: number; churnRisk: number; expansion: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎯 AI Success v7</h3>
    <div className="text-sm">{active}/{trackers} active · health {health} · {churnRisk}% churn risk · ${expansion.toLocaleString()} expansion</div>
  </div>);
}
