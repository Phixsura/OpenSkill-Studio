"use client";

interface Route { event_type: string; endpoint_url: string; priority: number; active: boolean; }
interface WebhookRoutingTableProps { routes: Route[]; onToggle: (index: number) => void; }

export function WebhookRoutingTable({ routes, onToggle }: WebhookRoutingTableProps) {
  if (routes.length === 0) return <p className="text-sm text-gray-400">No routing rules configured.</p>;
  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700">
      <table className="min-w-full text-sm">
        <thead className="bg-gray-50 dark:bg-gray-800">
          <tr>
            <th className="px-3 py-2 text-left">Event</th>
            <th className="px-3 py-2 text-left">Endpoint</th>
            <th className="px-3 py-2 text-center">Priority</th>
            <th className="px-3 py-2 text-center">Active</th>
          </tr>
        </thead>
        <tbody>
          {routes.map((r, i) => (
            <tr key={i} className="border-t dark:border-gray-700">
              <td className="px-3 py-2 font-mono text-xs">{r.event_type}</td>
              <td className="px-3 py-2 font-mono text-xs truncate max-w-[200px]">{r.endpoint_url}</td>
              <td className="px-3 py-2 text-center text-xs">{r.priority}</td>
              <td className="px-3 py-2 text-center">
                <button onClick={() => onToggle(i)} className={`rounded-full px-2 py-0.5 text-xs ${r.active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                  {r.active ? "ON" : "OFF"}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
