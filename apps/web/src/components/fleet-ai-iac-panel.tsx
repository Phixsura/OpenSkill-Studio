"use client";
export function FleetAiIacPanel({ systems, active, resources, applies, driftFree }: { systems: number; active: number; resources: number; applies: number; driftFree: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏗️ AI Infra as Code</h3>
    <div className="text-sm">{active}/{systems} active · {resources.toLocaleString()} resources · {applies} applies · {driftFree}% drift-free</div>
  </div>);
}
