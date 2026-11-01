"use client";
export function FleetAiContextPanel({ services, active, avgUtil, truncations }: { services: number; active: number; avgUtil: number; truncations: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📏 AI Context</h3>
    <div className="text-sm">{active}/{services} active · {avgUtil}% utilization · {truncations} truncations</div>
  </div>);
}
