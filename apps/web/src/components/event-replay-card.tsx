"use client";

interface StoredEventInfo {
  event_id: string;
  event_type: string;
  source: string;
  replayed: boolean;
}

interface EventReplayCardProps {
  events: StoredEventInfo[];
  eventTypes: string[];
  totalCount: number;
  appName: string;
}

export default function EventReplayCard({
  events,
  eventTypes,
  totalCount,
  appName,
}: EventReplayCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🔄 Event Replay
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {totalCount} events · {eventTypes.length} types
        </span>
      </div>

      {eventTypes.length > 0 && (
        <div className="mb-3 flex flex-wrap gap-1">
          {eventTypes.map((t) => (
            <span
              key={t}
              className="rounded bg-gray-100 px-1.5 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800"
            >
              {t}
            </span>
          ))}
        </div>
      )}

      {events.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No events stored</p>
      ) : (
        <div className="space-y-1">
          {events.map((e) => (
            <div
              key={e.event_id}
              className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800"
            >
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
                  {e.event_type}
                </span>
                <span className="text-[10px] text-gray-400">{e.source}</span>
              </div>
              {e.replayed && <span className="text-[10px] text-blue-500">replayed</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
