"use client";

interface Webhook { id: string; url: string; events: string[]; active: boolean; successRate: number; }
interface DeliveryStats { total: number; success: number; failed: number; successRate: number; }
interface WebhooksPageProps { appName: string; webhooks: Webhook[]; active: number;
  deliveryStats: DeliveryStats; health: string;
  onAdd: () => void; onToggle: (id: string) => void; onDelete: (id: string) => void; }

const healthIcons: Record<string, string> = { good: "🟢", warning: "🟡", critical: "🔴" };

export function WebhooksPage({ appName, webhooks, active, deliveryStats, health,
  onAdd, onToggle, onDelete }: WebhooksPageProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔗 {appName} — Webhooks</h2>
        <button onClick={onAdd} className="rounded bg-blue-600 px-4 py-1.5 text-sm text-white">+ Add Webhook</button>
      </div>
      <div className="grid grid-cols-4 gap-3">
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <span>{healthIcons[health]}</span>
          <p className="text-xs text-gray-400 mt-1">{health}</p>
        </div>
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-lg font-bold">{active}</p><p className="text-xs text-gray-400">Active</p>
        </div>
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-lg font-bold">{deliveryStats.successRate}%</p><p className="text-xs text-gray-400">Success</p>
        </div>
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-lg font-bold text-red-600">{deliveryStats.failed}</p><p className="text-xs text-gray-400">Failed</p>
        </div>
      </div>
      <div className="divide-y rounded-xl border dark:divide-gray-700 dark:border-gray-700">
        {webhooks.map(wh => (
          <div key={wh.id} className={`px-4 py-3 ${!wh.active ? "opacity-50" : ""}`}>
            <div className="flex items-center justify-between">
              <code className="text-sm font-mono truncate">{wh.url}</code>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400">{wh.successRate}%</span>
                <button onClick={() => onToggle(wh.id)} className="text-xs text-blue-600">{wh.active ? "Disable" : "Enable"}</button>
                <button onClick={() => onDelete(wh.id)} className="text-xs text-red-600">Delete</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
