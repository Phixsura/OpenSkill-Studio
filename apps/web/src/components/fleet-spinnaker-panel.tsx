"use client";
export function FleetSpinnakerPanel({ total, succeeded, failed, running, successRate }: { total: number; succeeded: number; failed: number; running: number; successRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎡 Spinnaker</h3>
    <div className="text-sm">{succeeded}✅ {failed}❌ {running}🔄 · {successRate}% success</div>
  </div>);
}
