"use client";

interface Event { event_type: string; version: number; timestamp: string; data: Record<string, unknown>; }
interface EventStreamViewerProps { events: Event[]; streamId: string; }

const EVENT_ICONS: Record<string, string> = { created: "🟢", updated: "🔵", deleted: "🔴" };

export function EventStreamViewer({ events, streamId }: EventStreamViewerProps) {
  if (events.length === 0) return <p className="text-sm text-gray-400">No events in stream.</p>;
  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="border-b p-3 dark:border-gray-700">
        <h3 className="text-sm font-semibold">Event Stream</h3>
        <p className="text-xs text-gray-400">{streamId} · {events.length} events</p>
      </div>
      <ul className="max-h-64 overflow-y-auto">
        {events.map(e => (
          <li key={e.version} className="flex items-center gap-2 border-b px-3 py-2 text-xs dark:border-gray-700">
            <span>{EVENT_ICONS[e.event_type] || "📌"}</span>
            <span className="font-medium">{e.event_type}</span>
            <span className="text-gray-400">v{e.version}</span>
            <span className="ml-auto text-gray-400">{e.timestamp.slice(0, 10)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
