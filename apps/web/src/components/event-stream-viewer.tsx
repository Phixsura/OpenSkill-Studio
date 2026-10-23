"use client";

interface Event { event_id: string; type: string; source: string; timestamp: string; payload: Record<string, unknown>; }
interface EventStreamViewerProps { events: Event[]; hasMore: boolean; onLoadMore: () => void; }

const typeIcons: Record<string, string> = {
  "app.installed": "📥", "app.uninstalled": "📤", "app.updated": "🔄",
  "review.created": "⭐", "webhook.delivered": "✅", "webhook.failed": "❌",
  "payment.completed": "💰", "user.signup": "👤",
};

export function EventStreamViewer({ events, hasMore, onLoadMore }: EventStreamViewerProps) {
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Event Stream</h2>
      <div className="space-y-1">
        {events.map(e => (
          <div key={e.event_id} className="flex items-center gap-3 rounded border px-3 py-2 font-mono text-xs dark:border-gray-700">
            <span>{typeIcons[e.type] ?? "📌"}</span>
            <span className="font-medium text-blue-600 dark:text-blue-400">{e.type}</span>
            <span className="text-gray-400">{e.source}</span>
            <span className="ml-auto text-gray-300">{new Date(e.timestamp).toLocaleTimeString()}</span>
          </div>
        ))}
      </div>
      {hasMore && (
        <button onClick={onLoadMore} className="w-full rounded border py-1.5 text-xs text-gray-500 dark:border-gray-700">
          Load More Events
        </button>
      )}
    </div>
  );
}
