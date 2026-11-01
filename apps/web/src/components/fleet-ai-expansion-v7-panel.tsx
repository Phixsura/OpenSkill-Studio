"use client";
export function FleetAiExpansionV7Panel({ trackers, active, markets, features, expansion }: { trackers: number; active: number; markets: number; features: number; expansion: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌍 AI Expansion v7</h3>
    <div className="text-sm">{active}/{trackers} active · {markets} markets · {features} features · ${expansion.toLocaleString()} expansion</div>
  </div>);
}
