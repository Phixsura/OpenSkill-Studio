"use client";

interface LogEvent { category: string; event_type: string; actor_id: string; timestamp: string; app_id?: string; }
interface ActivityLogViewerProps { events: LogEvent[]; onFilter: (category: string | null) => void; activeFilter: string | null; }

const CAT_ICONS: Record<string, string> = { app: "📦", install: "📥", webhook: "🔗", auth: "🔐", team: "👥" };

export function ActivityLogViewer({ events, onFilter, activeFilter }: ActivityLogViewerProps) {
  const categories = ["app", "install", "webhook", "auth", "team"];
  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="flex items-center gap-1 border-b p-3 dark:border-gray-700">
        <button onClick={() => onFilter(null)} className={`rounded px-2 py-1 text-xs ${!activeFilter ? "bg-blue-100 font-semibold" : "text-gray-500"}`}>All</button>
        {categories.map(c => (
          <button key={c} onClick={() => onFilter(c)} className={`rounded px-2 py-1 text-xs ${activeFilter === c ? "bg-blue-100 font-semibold" : "text-gray-500"}`}>
            {CAT_ICONS[c]} {c}
          </button>
        ))}
      </div>
      <ul className="max-h-64 overflow-y-auto">
        {events.length === 0 ? <li className="p-4 text-center text-sm text-gray-400">No events</li> :
          events.map((e, i) => (
            <li key={i} className="flex items-center gap-2 border-b px-3 py-2 text-xs dark:border-gray-700">
              <span>{CAT_ICONS[e.category] || "📌"}</span>
              <span className="font-medium">{e.event_type}</span>
              <span className="text-gray-400">{e.actor_id}</span>
              <span className="ml-auto text-gray-400">{e.timestamp.slice(11, 16)}</span>
            </li>
          ))}
      </ul>
    </div>
  );
}
