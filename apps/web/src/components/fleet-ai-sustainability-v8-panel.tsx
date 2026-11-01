"use client";
export function FleetAiSustainabilityV8Panel({ trackers, active, carbon, renewable, pue }: { trackers: number; active: number; carbon: number; renewable: number; pue: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌱 AI Sustainability v8</h3>
    <div className="text-sm">{active}/{trackers} active · {carbon}kg CO₂ · {renewable}% renewable · PUE {pue}</div>
  </div>);
}
