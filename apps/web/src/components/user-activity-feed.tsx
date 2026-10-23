"use client";

interface ActivityEntry { action: string; resource: string; details: string; timestamp: number; }
interface UserActivityFeedProps { entries: ActivityEntry[]; userName: string; }

const ACTION_ICON: Record<string, string> = {
  create: "✨", deploy: "🚀", update: "📝", delete: "🗑️", login: "🔑",
};

export function UserActivityFeed({ entries, userName }: UserActivityFeedProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Activity</h3>
        <p className="text-xs text-gray-400">{userName} · {entries.length} actions</p>
      </div>
      <div className="divide-y dark:divide-gray-700 max-h-64 overflow-y-auto">
        {entries.map((e, i) => (
          <div key={i} className="flex gap-2 px-4 py-2 text-sm">
            <span>{ACTION_ICON[e.action] || "📌"}</span>
            <div>
              <span className="capitalize font-medium">{e.action}</span>
              <span className="text-gray-400 ml-1">{e.resource}</span>
              {e.details && <p className="text-xs text-gray-400">{e.details}</p>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
