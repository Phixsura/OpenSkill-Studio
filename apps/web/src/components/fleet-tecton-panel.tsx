"use client";
export function FleetTectonPanel({ workspaces, active, features, servesPerSec }: { workspaces: number; active: number; features: number; servesPerSec: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ Tecton</h3>
    <div className="text-sm">{active}/{workspaces} active · {features} features · {servesPerSec.toLocaleString()} serves/s</div>
  </div>);
}
