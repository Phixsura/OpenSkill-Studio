"use client";
export function FleetStepfnPanel({ machines, active, running, succeeded, failed }: { machines: number; active: number; running: number; succeeded: number; failed: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 Step Functions</h3>
    <div className="text-sm">{active}/{machines} active · {running} running · {succeeded}✅ {failed}❌/24h</div>
  </div>);
}
