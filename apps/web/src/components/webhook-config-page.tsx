"use client";

interface Webhook { id: string; url: string; events: string[]; eventCount: number;
  active: boolean; successRate: number; }
interface WebhookConfigPageProps { webhooks: Webhook[]; active: number; canAdd: boolean;
  totalEventTypes: number; onAdd: () => void; onToggle: (id: string) => void; onDelete: (id: string) => void; }

export function WebhookConfigPage({ webhooks, active, canAdd, totalEventTypes,
  onAdd, onToggle, onDelete }: WebhookConfigPageProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold">🔗 Webhooks</h2>
          <p className="text-xs text-gray-400">{active} active · {totalEventTypes} event types available</p>
        </div>
        {canAdd && <button onClick={onAdd} className="rounded bg-blue-600 px-4 py-2 text-sm text-white">+ Add Webhook</button>}
      </div>
      {webhooks.length === 0 ? (
        <div className="py-12 text-center">
          <span className="text-4xl">🔗</span>
          <p className="mt-2 text-sm text-gray-500">No webhooks configured yet</p>
          <button onClick={onAdd} className="mt-3 rounded bg-blue-600 px-4 py-2 text-sm text-white">Create First Webhook</button>
        </div>
      ) : (
        <div className="divide-y rounded-xl border dark:divide-gray-700 dark:border-gray-700">
          {webhooks.map(wh => (
            <div key={wh.id} className={`px-4 py-3 ${!wh.active ? "opacity-50" : ""}`}>
              <div className="flex items-center justify-between">
                <div>
                  <code className="text-sm font-mono">{wh.url}</code>
                  <div className="mt-1 flex gap-1">
                    {wh.events.slice(0, 3).map(e => (
                      <span key={e} className="rounded bg-blue-100 px-1.5 py-0.5 text-xs text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">{e}</span>
                    ))}
                    {wh.eventCount > 3 && <span className="text-xs text-gray-400">+{wh.eventCount - 3}</span>}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-400">{wh.successRate}%</span>
                  <button onClick={() => onToggle(wh.id)} className="text-xs text-blue-600">{wh.active ? "Disable" : "Enable"}</button>
                  <button onClick={() => onDelete(wh.id)} className="text-xs text-red-600">Delete</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
