"use client";
export function FleetArgoWfPanel({ total, succeeded, failed, running, avgDuration }: { total: number; succeeded: number; failed: number; running: number; avgDuration: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔧 Argo Workflows</h3>
    <div className="text-sm">{succeeded}✅ {failed}❌ {running}🔄 · avg {avgDuration}min</div>
  </div>);
}
