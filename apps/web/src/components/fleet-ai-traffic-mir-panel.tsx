"use client";
export function FleetAiTrafficMirPanel({ mirrors, active, mirrored, targets, overhead }: { mirrors: number; active: number; mirrored: number; targets: number; overhead: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🪞 AI Traffic Mirror</h3>
    <div className="text-sm">{active}/{mirrors} active · {mirrored.toLocaleString()} mirrored · {targets} targets · {overhead}% overhead</div>
  </div>);
}
