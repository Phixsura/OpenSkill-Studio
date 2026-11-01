"use client";
export function FleetPackerPanel({ total, succeeded, failed, avgDuration }: { total: number; succeeded: number; failed: number; avgDuration: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📀 Packer</h3>
    <div className="text-sm">{succeeded}✅ {failed}❌ · avg {avgDuration}min</div>
  </div>);
}
