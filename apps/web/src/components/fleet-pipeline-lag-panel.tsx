"use client";
export function FleetPipelineLagPanel({ total, lagging, maxLag, fresh }: { total: number; lagging: number; maxLag: number; fresh: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 Pipeline Lag</h3>
    {fresh ? <span className="text-xs text-green-600">✅ All {total} pipelines fresh</span>
     : <span className="text-xs text-yellow-600">⚠️ {lagging} lagging · max {maxLag}min</span>}
  </div>);
}
