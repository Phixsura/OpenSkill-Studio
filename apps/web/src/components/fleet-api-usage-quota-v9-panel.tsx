"use client";
export function FleetApiUsageQuotaV9Panel({ consumers, overQuota }: { consumers: number; overQuota: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📏 API Usage Quota v9</h3>
    <div className="text-sm">{consumers} consumers · {overQuota} over quota</div>
  </div>);
}
