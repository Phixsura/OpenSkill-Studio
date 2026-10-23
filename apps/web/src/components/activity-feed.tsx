"use client";

interface Activity { id: string; actor: string; verb: string; target: string; icon: string; timestamp: string; }
interface ActivityFeedProps { activities: Activity[]; hasMore: boolean; onLoadMore: () => void; }

export function ActivityFeed({ activities, hasMore, onLoadMore }: ActivityFeedProps) {
  return (
    <div className="space-y-1">
      <h3 className="text-sm font-semibold mb-3">Activity</h3>
      {activities.map(a => (
        <div key={a.id} className="flex items-start gap-2.5 py-2">
          <span className="mt-0.5 text-sm">{a.icon}</span>
          <div className="flex-1 min-w-0">
            <p className="text-sm">
              <span className="font-medium">{a.actor}</span>{" "}
              <span className="text-gray-500">{a.verb}</span>{" "}
              <span className="font-medium">{a.target}</span>
            </p>
            <time className="text-xs text-gray-400">{new Date(a.timestamp).toLocaleString()}</time>
          </div>
        </div>
      ))}
      {hasMore && (
        <button onClick={onLoadMore} className="w-full rounded border py-2 text-xs text-gray-500 hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800">
          Load more
        </button>
      )}
    </div>
  );
}
