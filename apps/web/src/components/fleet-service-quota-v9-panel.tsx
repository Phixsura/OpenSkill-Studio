"use client";
export function FleetServiceQuotaV9Panel({ quotas, nearLimit }: { quotas: number; nearLimit: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📏 Service Quota v9</h3>
    <div className="text-sm">{quotas} quotas · {nearLimit} near limit</div>
  </div>);
}
