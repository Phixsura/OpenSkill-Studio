"use client";
export function FleetDeployPipePanel({ total, passing, failing, avgDuration, healthy }: { total: number; passing: number; failing: number; avgDuration: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔧 CI/CD Pipelines</h3>
    <div className="text-sm">{passing}✅ {failing}❌ · avg {avgDuration}min</div>
    {!healthy && <span className="text-xs text-red-500">⚠️ {failing} failing pipelines</span>}
  </div>);
}
