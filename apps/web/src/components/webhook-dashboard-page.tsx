"use client";

interface Endpoint { url: string; active: boolean; events: string[]; }
interface Deliveries { total: number; success: number; failed: number; successRate: number; }
interface WebhookDashboardPageProps { endpoints: Endpoint[]; activeEndpoints: number;
  deliveries: Deliveries; health: string; period: string; }

const healthConfig: Record<string, { icon: string; label: string }> = {
  good: { icon: "🟢", label: "Healthy" }, warning: { icon: "🟡", label: "Warning" },
  critical: { icon: "🔴", label: "Critical" },
};

export function WebhookDashboardPage({ endpoints, activeEndpoints, deliveries, health, period }: WebhookDashboardPageProps) {
  const h = healthConfig[health] ?? healthConfig.good;
  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔗 Webhooks</h2>
        <div className="flex items-center gap-2">
          <span>{h.icon}</span>
          <span className="text-xs text-gray-400">{h.label} · {period}</span>
        </div>
      </div>
      <div className="grid grid-cols-4 gap-3">
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-xl font-bold">{activeEndpoints}</p><p className="text-xs text-gray-400">Endpoints</p>
        </div>
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-xl font-bold text-green-600">{deliveries.success}</p><p className="text-xs text-gray-400">Delivered</p>
        </div>
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-xl font-bold text-red-600">{deliveries.failed}</p><p className="text-xs text-gray-400">Failed</p>
        </div>
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-xl font-bold">{deliveries.successRate}%</p><p className="text-xs text-gray-400">Success Rate</p>
        </div>
      </div>
      <div className="space-y-2">
        {endpoints.map((ep, i) => (
          <div key={i} className="flex items-center justify-between rounded-lg border px-4 py-2 dark:border-gray-700">
            <code className="text-sm font-mono truncate">{ep.url}</code>
            <span className={`text-xs ${ep.active ? "text-green-600" : "text-gray-400"}`}>{ep.active ? "Active" : "Inactive"}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
