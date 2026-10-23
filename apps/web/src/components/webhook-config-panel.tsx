"use client";

interface WebhookItem { id: string; url: string; eventCount: number; active: boolean;
  secure: boolean; lastDelivery: string; successRate: number; }
interface WebhookConfigPanelProps { webhooks: WebhookItem[]; activeCount: number;
  allSecure: boolean; onAdd: () => void; onToggle: (id: string) => void; onEdit: (id: string) => void; }

export function WebhookConfigPanel({ webhooks, activeCount, allSecure, onAdd, onToggle, onEdit }: WebhookConfigPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <div>
          <h3 className="font-semibold">🔗 Webhooks</h3>
          <p className="text-xs text-gray-400">{activeCount} active{!allSecure && " · ⚠️ Insecure endpoints"}</p>
        </div>
        <button onClick={onAdd} className="text-xs px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700">+ Add Webhook</button>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {webhooks.map(wh => (
          <div key={wh.id} className="flex items-center justify-between px-4 py-3">
            <div>
              <div className="flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${wh.active ? "bg-green-500" : "bg-gray-300"}`} />
                <span className="text-sm font-mono truncate max-w-xs">{wh.url}</span>
                {!wh.secure && <span className="text-xs text-red-500">⚠️</span>}
              </div>
              <div className="flex gap-2 text-xs text-gray-400 mt-0.5">
                <span>{wh.eventCount} events</span>
                <span>Last: {wh.lastDelivery}</span>
                <span>{wh.successRate}% success</span>
              </div>
            </div>
            <div className="flex gap-1">
              <button onClick={() => onEdit(wh.id)} className="text-xs px-2 py-1 border rounded hover:bg-gray-50">Edit</button>
              <button onClick={() => onToggle(wh.id)} className="text-xs px-2 py-1 border rounded hover:bg-gray-50">
                {wh.active ? "Disable" : "Enable"}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
