"use client";
export function FleetResourceQuotaV9Panel({ quotas, cpuUsed }: { quotas: number; cpuUsed: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📏 Resource Quota v9</h3>
    <div className="text-sm">{quotas} quotas · {cpuUsed} CPU used</div>
  </div>);
}
