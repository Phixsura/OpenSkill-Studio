"use client";
export function FleetGcpDmPanel({ total, done, failed }: { total: number; done: number; failed: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☁️ GCP DM</h3>
    <div className="text-sm">{done}✅ {failed}❌ of {total}</div>
  </div>);
}
