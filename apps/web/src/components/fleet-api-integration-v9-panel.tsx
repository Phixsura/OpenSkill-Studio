"use client";
export function FleetApiIntegrationV9Panel({ integrations, calls }: { integrations: number; calls: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔌 API Integration v9</h3>
    <div className="text-sm">{integrations} integrations · {calls.toLocaleString()} calls</div>
  </div>);
}
