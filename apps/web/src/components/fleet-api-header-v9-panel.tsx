"use client";
export function FleetApiHeaderV9Panel({ policies, security }: { policies: number; security: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 API Header v9</h3>
    <div className="text-sm">{policies} policies · {security} security</div>
  </div>);
}
