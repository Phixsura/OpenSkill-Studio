"use client";
export function FleetApiKeyMgrV9Panel({ total, active }: { total: number; active: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔑 API Key Manager v9</h3>
    <div className="text-sm">{total} keys · {active} active</div>
  </div>);
}
