"use client";

interface Activity { actor: string; action: string; target: string; }
interface ActivityFeedTimelineProps { items: Activity[]; count: number;
  byAction: Record<string, number>; }

const ACTION_ICONS: Record<string, string> = {
  deployed: "🚀", reviewed: "👁️", created: "✨", updated: "📝",
  deleted: "🗑️", approved: "✅", commented: "💬",
};

export function ActivityFeedTimeline({ items, count, byAction }: ActivityFeedTimelineProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📰 Activity Feed</h3>
        <span className="text-xs text-gray-400">{count} activities</span>
      </div>
      <div className="divide-y dark:divide-gray-700 max-h-64 overflow-y-auto">
        {items.map((a, i) => (
          <div key={i} className="flex items-start gap-2 px-4 py-2.5">
            <span className="text-lg">{ACTION_ICONS[a.action] ?? "⚪"}</span>
            <div className="text-sm">
              <span className="font-medium">{a.actor}</span>{" "}
              <span className="text-gray-400">{a.action}</span>{" "}
              <span className="font-mono text-xs">{a.target}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
