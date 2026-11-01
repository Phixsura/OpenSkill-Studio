"use client";

interface Activity { user_id: string; action: string; resource: string; timestamp: string; }
interface ActivityTimelineProps { activities: Activity[]; totalActivities: number; uniqueUsers: number; }

const actionIcons: Record<string, string> = {
  view: "👁️", install: "📥", uninstall: "📤", review: "⭐",
  deploy: "🚀", update: "🔄", create: "➕", delete: "🗑️",
};

export function ActivityTimeline({ activities, totalActivities, uniqueUsers }: ActivityTimelineProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Activity Timeline</h2>
        <span className="text-xs text-gray-400">{totalActivities} actions · {uniqueUsers} users</span>
      </div>
      <div className="relative border-l-2 border-gray-200 pl-6 dark:border-gray-700">
        {activities.map((a, i) => (
          <div key={i} className="relative mb-4">
            <div className="absolute -left-[1.9rem] flex h-4 w-4 items-center justify-center rounded-full bg-blue-500 text-[8px] text-white">
              {actionIcons[a.action]?.slice(0, 2) ?? "•"}
            </div>
            <div>
              <p className="text-sm">
                <strong>{a.user_id}</strong> {a.action} <span className="text-gray-400">{a.resource}</span>
              </p>
              <p className="text-xs text-gray-400">{new Date(a.timestamp).toLocaleString()}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
