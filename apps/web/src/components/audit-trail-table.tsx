"use client";

interface AuditEvent { id: string; actor: string; action: string; resource: string;
  details: string; ip: string; }
interface AuditTrailTableProps { events: AuditEvent[]; totalEvents: number; }

const ACTION_COLOR: Record<string, string> = {
  create: "bg-green-100 text-green-700", update: "bg-blue-100 text-blue-700",
  delete: "bg-red-100 text-red-700", login: "bg-purple-100 text-purple-700",
};

export function AuditTrailTable({ events, totalEvents }: AuditTrailTableProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📜 Audit Trail</h3>
        <span className="text-xs text-gray-400">{totalEvents} events</span>
      </div>
      <table className="w-full text-sm">
        <thead><tr className="text-xs text-gray-400 border-b dark:border-gray-700">
          <th className="p-3 text-left">Actor</th><th className="p-3">Action</th>
          <th className="p-3 text-left">Resource</th><th className="p-3 text-left">Details</th>
        </tr></thead>
        <tbody>
          {events.map(e => (
            <tr key={e.id} className="border-b last:border-0 dark:border-gray-700">
              <td className="p-3 font-medium">{e.actor}</td>
              <td className="p-3 text-center">
                <span className={`text-xs px-1.5 py-0.5 rounded ${ACTION_COLOR[e.action] || "bg-gray-100"}`}>{e.action}</span>
              </td>
              <td className="p-3 font-mono text-xs">{e.resource}</td>
              <td className="p-3 text-xs text-gray-400 max-w-xs truncate">{e.details}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
