"use client";

interface ActivityEvent {
  eventId: string;
  extensionId: string;
  eventType: string;
  actor: string;
  message: string;
  timestamp: string;
}

const typeIcons: Record<string, string> = {
  install: "📥", uninstall: "📤", review: "⭐", deploy: "🚀",
  update: "🔄", publish: "📦",
};

export function ActivityFeedPanel({
  events,
  onFilter,
}: {
  events: ActivityEvent[];
  onFilter?: (type: string | null) => void;
}) {
  const types = [...new Set(events.map((e) => e.eventType))].sort();

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">📰 Activity Feed</h2>
      <div className="flex gap-1 flex-wrap">
        <button onClick={() => onFilter?.(null)}
          className="text-xs px-2.5 py-1 rounded-full bg-blue-600 text-white">All</button>
        {types.map((t) => (
          <button key={t} onClick={() => onFilter?.(t)}
            className="text-xs px-2.5 py-1 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-500">
            {typeIcons[t] || "●"} {t}
          </button>
        ))}
      </div>
      <div className="space-y-1">
        {events.map((e) => (
          <div key={e.eventId} className="rounded-lg border dark:border-gray-700 p-2 flex items-center gap-2 text-sm">
            <span>{typeIcons[e.eventType] || "●"}</span>
            <span className="flex-1">{e.message}</span>
            <span className="text-xs text-gray-400">{e.actor} · {e.timestamp}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
