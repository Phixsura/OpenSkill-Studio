"use client";
export function FleetAiCfgDriftPanel({ detectors, active, resources, drifts, remediated }: { detectors: number; active: number; resources: number; drifts: number; remediated: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 AI Config Drift</h3>
    <div className="text-sm">{active}/{detectors} active · {resources.toLocaleString()} resources · {drifts} drifts · {remediated} fixed</div>
  </div>);
}
