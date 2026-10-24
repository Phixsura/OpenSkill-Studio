"use client";

interface Event { seq: number; type: string; aggregateId: string; }
interface EventSourcingViewerProps { events: Event[]; totalEvents: number;
  aggregates: number; byType: Record<string, number>; }

export function EventSourcingViewer({ events, totalEvents, aggregates, byType }: EventSourcingViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📜 Event Store</h3>
        <span className="text-xs text-gray-400">{totalEvents} events · {aggregates} aggregates</span>
      </div>
      <div className="flex gap-2 px-4 py-1.5 border-b dark:border-gray-700 text-[10px]">
        {Object.entries(byType).map(([t, c]) => (
          <span key={t} className="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 rounded">{t}: {c}</span>
        ))}
      </div>
      <div className="divide-y dark:divide-gray-700 max-h-40 overflow-y-auto">
        {events.map(e => (
          <div key={e.seq} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className="text-gray-400">#{e.seq}</span>
              <span className="font-mono text-blue-500">{e.type}</span>
            </div>
            <span className="text-gray-400 font-mono">{e.aggregateId}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
