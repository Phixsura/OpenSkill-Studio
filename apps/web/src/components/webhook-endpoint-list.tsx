"use client";

interface Endpoint { id: string; url: string; events: string[]; active: boolean; description: string; }
interface WebhookEndpointListProps { endpoints: Endpoint[]; active: number; onToggle: (id: string) => void; onDelete: (id: string) => void; }

export function WebhookEndpointList({ endpoints, active, onToggle, onDelete }: WebhookEndpointListProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Webhook Endpoints</h3>
        <span className="text-xs text-gray-400">{active} active</span>
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {endpoints.map(e => (
          <div key={e.id} className={`px-4 py-3 ${!e.active ? "opacity-50" : ""}`}>
            <div className="flex items-center justify-between">
              <div className="min-w-0">
                <code className="text-sm font-mono truncate block">{e.url}</code>
                {e.description && <p className="text-xs text-gray-400">{e.description}</p>}
                <div className="mt-1 flex gap-1">{e.events.slice(0, 3).map(ev => (
                  <span key={ev} className="rounded bg-blue-100 px-1.5 py-0.5 text-xs text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">{ev}</span>
                ))}{e.events.length > 3 && <span className="text-xs text-gray-400">+{e.events.length - 3}</span>}</div>
              </div>
              <div className="flex items-center gap-2 shrink-0 ml-3">
                <button onClick={() => onToggle(e.id)} className="text-xs text-blue-600">{e.active ? "Disable" : "Enable"}</button>
                <button onClick={() => onDelete(e.id)} className="text-xs text-red-600">Delete</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
