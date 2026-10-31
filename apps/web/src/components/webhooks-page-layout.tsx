"use client";

interface WebhooksOverview { total_endpoints: number; active: number; delivery_rate: number; total_deliveries: number; }
interface WebhooksPageLayoutProps { appName: string; overview: WebhooksOverview; onAddEndpoint: () => void; children: React.ReactNode; }

export function WebhooksPageLayout({ appName, overview, onAddEndpoint, children }: WebhooksPageLayoutProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">{appName} Webhooks</h1>
        <button onClick={onAddEndpoint} className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white">+ Add Endpoint</button>
      </div>
      <div className="grid grid-cols-4 gap-3">
        <div className="rounded-lg border border-gray-200 p-3 text-center dark:border-gray-700">
          <p className="text-xl font-bold">{overview.total_endpoints}</p><p className="text-xs text-gray-400">Endpoints</p>
        </div>
        <div className="rounded-lg border border-gray-200 p-3 text-center dark:border-gray-700">
          <p className="text-xl font-bold text-green-600">{overview.active}</p><p className="text-xs text-gray-400">Active</p>
        </div>
        <div className="rounded-lg border border-gray-200 p-3 text-center dark:border-gray-700">
          <p className={`text-xl font-bold ${overview.delivery_rate >= 99 ? "text-green-600" : "text-yellow-600"}`}>{overview.delivery_rate}%</p>
          <p className="text-xs text-gray-400">Delivery Rate</p>
        </div>
        <div className="rounded-lg border border-gray-200 p-3 text-center dark:border-gray-700">
          <p className="text-xl font-bold">{overview.total_deliveries.toLocaleString()}</p><p className="text-xs text-gray-400">Deliveries</p>
        </div>
      </div>
      <div>{children}</div>
    </div>
  );
}
