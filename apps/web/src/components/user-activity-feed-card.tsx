"use client";

interface ActivityInfo {
  event_id: string;
  user_id: string;
  action: string;
  resource_type: string;
  resource_id: string;
  description: string;
  timestamp: string;
}

interface UserActivityFeedCardProps {
  activities: ActivityInfo[];
  appName: string;
}

const ACTION_ICONS: Record<string, string> = {
  created: "➕",
  updated: "✏️",
  deleted: "🗑️",
  viewed: "👁️",
};

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  if (diff < 60_000) return "just now";
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`;
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)}h ago`;
  return `${Math.floor(diff / 86_400_000)}d ago`;
}

export default function UserActivityFeedCard({ activities, appName }: UserActivityFeedCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Activity Feed</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{activities.length} events</span>
      </div>

      {activities.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No activity</p>
      ) : (
        <div className="space-y-1.5">
          {activities.map((a) => (
            <div
              key={a.event_id}
              className="flex items-start gap-2 rounded px-2 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-800/50"
            >
              <span className="mt-0.5">{ACTION_ICONS[a.action] ?? "📌"}</span>
              <div className="min-w-0 flex-1">
                <div className="text-xs">
                  <span className="font-medium text-gray-800 dark:text-gray-200">{a.user_id}</span>
                  <span className="text-gray-500"> {a.action} </span>
                  <span className="text-gray-600 dark:text-gray-400">
                    {a.resource_type}/{a.resource_id}
                  </span>
                </div>
                {a.description && <p className="text-[11px] text-gray-400">{a.description}</p>}
              </div>
              <span className="shrink-0 text-[10px] text-gray-400">{timeAgo(a.timestamp)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
