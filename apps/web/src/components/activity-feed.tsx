"use client";

interface Activity { action: string; resource: string; details: string; timestamp: string; }

interface ActivityFeedProps { activities: Activity[]; }

const ACTION_ICONS: Record<string, string> = {
  create_app: "📦", publish: "🚀", submit_review: "📝", create_version: "🏷️",
  install: "📥", uninstall: "🗑️", edit: "✏️", delete: "❌", revoke: "🚫",
};

export function ActivityFeed({ activities }: ActivityFeedProps) {
  if (activities.length === 0) return <p className="py-4 text-center text-sm text-gray-400">No recent activity</p>;
  return (
    <div className="space-y-2">
      {activities.map((a, i) => (
        <div key={i} className="flex items-start gap-2 rounded border border-gray-200 p-2 text-sm dark:border-gray-700">
          <span>{ACTION_ICONS[a.action] ?? "•"}</span>
          <div className="flex-1">
            <span className="font-medium">{a.action.replace(/_/g, " ")}</span>
            <span className="ml-1 text-gray-500">{a.resource}</span>
            {a.details && <p className="text-xs text-gray-400">{a.details}</p>}
          </div>
          <span className="text-xs text-gray-400">{a.timestamp}</span>
        </div>
      ))}
    </div>
  );
}
