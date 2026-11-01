"use client";

interface AuditEvent { action: string; icon: string; actor: string; target: string;
  ip: string; timestamp: string; }
interface AuditLogPageProps { events: AuditEvent[]; total: number; page: number;
  totalPages: number; availableActions: string[]; availableActors: string[];
  onFilter: (action: string | null, actor: string | null) => void;
  onPageChange: (page: number) => void; }

export function AuditLogPage({ events, total, page, totalPages, availableActions,
  availableActors, onFilter, onPageChange }: AuditLogPageProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📋 Audit Log</h2>
        <span className="text-xs text-gray-400">{total} events</span>
      </div>
      <div className="flex gap-2">
        <select onChange={e => onFilter(e.target.value || null, null)}
          className="rounded border px-2 py-1 text-xs dark:bg-gray-800 dark:border-gray-600">
          <option value="">All Actions</option>
          {availableActions.map(a => <option key={a} value={a}>{a}</option>)}
        </select>
        <select onChange={e => onFilter(null, e.target.value || null)}
          className="rounded border px-2 py-1 text-xs dark:bg-gray-800 dark:border-gray-600">
          <option value="">All Users</option>
          {availableActors.map(a => <option key={a} value={a}>{a}</option>)}
        </select>
      </div>
      <div className="divide-y rounded-xl border dark:divide-gray-700 dark:border-gray-700">
        {events.map((e, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-2.5">
            <div className="flex items-center gap-2">
              <span>{e.icon}</span>
              <span className="text-sm"><strong>{e.actor}</strong> {e.action.replace("_", " ")}</span>
              {e.target && <span className="text-xs text-gray-400">→ {e.target}</span>}
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-400">
              {e.ip && <span className="font-mono">{e.ip}</span>}
              <span>{e.timestamp}</span>
            </div>
          </div>
        ))}
      </div>
      <div className="flex justify-center gap-1 text-xs">
        <button onClick={() => onPageChange(page - 1)} disabled={page <= 1} className="rounded border px-2 py-1 disabled:opacity-30 dark:border-gray-700">←</button>
        <span className="px-2 py-1">{page}/{totalPages}</span>
        <button onClick={() => onPageChange(page + 1)} disabled={page >= totalPages} className="rounded border px-2 py-1 disabled:opacity-30 dark:border-gray-700">→</button>
      </div>
    </div>
  );
}
