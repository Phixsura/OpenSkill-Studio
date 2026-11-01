"use client";
export function FleetAiShadowTstPanel({ shadows, active, mirrored, divergence }: { shadows: number; active: number; mirrored: number; divergence: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👤 AI Shadow Testing</h3>
    <div className="text-sm">{active}/{shadows} active · {mirrored.toLocaleString()} mirrored · {divergence}% divergence</div>
  </div>);
}
