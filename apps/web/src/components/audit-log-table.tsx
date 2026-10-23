"use client";

interface AuditEntry { log_id: string; actor_id: string; action: string; resource_type: string; resource_id: string; timestamp: string; }
interface AuditLogTableProps { entries: AuditEntry[]; total: number; onFilter: (field: string, value: string) => void; }

export function AuditLogTable({ entries, total, onFilter }: AuditLogTableProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Audit Log</h2>
        <span className="text-sm text-gray-400">{total} entries</span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-xs text-gray-400 dark:border-gray-700">
              <th className="pb-2">Time</th><th className="pb-2">Actor</th>
              <th className="pb-2">Action</th><th className="pb-2">Resource</th>
            </tr>
          </thead>
          <tbody>
            {entries.map(e => (
              <tr key={e.log_id} className="border-b dark:border-gray-800">
                <td className="py-2 text-xs text-gray-400">{new Date(e.timestamp).toLocaleString()}</td>
                <td className="py-2">
                  <button onClick={() => onFilter("actor", e.actor_id)} className="text-blue-600 hover:underline">{e.actor_id}</button>
                </td>
                <td className="py-2 font-mono text-xs">{e.action}</td>
                <td className="py-2 text-xs text-gray-400">{e.resource_type}/{e.resource_id}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
