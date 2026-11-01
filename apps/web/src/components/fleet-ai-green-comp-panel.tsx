"use client";
export function FleetAiGreenCompPanel({ trackers, active, co2, kwh, renewable }: { trackers: number; active: number; co2: number; kwh: number; renewable: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌱 AI Green Computing</h3>
    <div className="text-sm">{active}/{trackers} active · {co2}kg CO₂ · {kwh} kWh · {renewable}% renewable</div>
  </div>);
}
