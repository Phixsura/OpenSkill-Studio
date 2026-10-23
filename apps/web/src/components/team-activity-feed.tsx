"use client";

interface Activity { id: string; actor: string; action: string; target: string; type: string; timestamp: string; }
interface TeamActivityFeedProps { activities: Activity[]; hasMore: boolean; onLoadMore: () => void; }

const typeIcons: Record<string, string> = {
  release: "🚀", code: "💻", review: "💬", config: "⚙️", incident: "🔥",
};

export function TeamActivityFeed({ activities, hasMore, onLoadMore }: TeamActivityFeedProps) {
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Team Activity</h2>
      <div className="space-y-2">
        {activities.map(a => (
          <div key={a.id} className="flex items-start gap-3 rounded-lg border p-3 dark:border-gray-700">
            <span className="text-lg">{typeIcons[a.type] ?? "📌"}</span>
            <div className="flex-1">
              <p className="text-sm">
                <strong>{a.actor}</strong> {a.action} <span className="text-gray-500">{a.target}</span>
              </p>
              <p className="text-xs text-gray-400">{new Date(a.timestamp).toLocaleString()}</p>
            </div>
          </div>
        ))}
      </div>
      {hasMore && (
        <button onClick={onLoadMore} className="w-full rounded border py-2 text-sm text-gray-500 dark:border-gray-700">
          Load More
        </button>
      )}
    </div>
  );
}
