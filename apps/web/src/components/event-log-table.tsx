"use client";

interface LogEvent { id: string; type: string; source: string; actor: string; }
interface EventLogTableProps { events: LogEvent[]; countByType: Record<string, number>; }

export function EventLogTable({ events, countByType }: EventLogTableProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📜 Event Log</h3>
        <div className="flex gap-2 text-xs">
          {Object.entries(countByType).map(([t, c]) => (
            <span key={t} className="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 rounded">{t}: {c}</span>
          ))}
        </div>
      </div>
      <div className="max-h-64 overflow-y-auto">
        {events.map(e => (
          <div key={e.id} className="flex items-center gap-3 px-4 py-2 text-sm border-b last:border-0 dark:border-gray-800">
            <span className="font-mono text-xs text-gray-400 w-24 truncate">{e.id}</span>
            <span className="text-xs px-1.5 py-0.5 bg-blue-100 dark:bg-blue-900/20 text-blue-700 rounded">{e.type}</span>
            <span className="text-xs text-gray-400">{e.source}</span>
            {e.actor && <span className="text-xs text-gray-400 ml-auto">{e.actor}</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
