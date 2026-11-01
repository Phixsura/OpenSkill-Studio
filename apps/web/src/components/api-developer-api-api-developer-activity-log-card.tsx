"use client";

interface ActivityInfo { activity_id: string; developer_id: string; action: string; resource: string; }
interface Props { activities: ActivityInfo[]; totalCount: number; appName: string; }

const aIcon: Record<string, string> = { key_created: "🔑", key_revoked: "🚫", app_created: "📱", webhook_configured: "🪝", settings_changed: "⚙️", team_joined: "👥", login: "🔓", logout: "🔒" };

export default function APIDeveloperAPIApiDeveloperActivityLogCard({ activities, totalCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📋 Activity Log</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-[10px] text-gray-400">{totalCount.toLocaleString()} events</span>
      </div>
      {activities.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No activity</p>
      ) : (
        <div className="space-y-1">
          {activities.map((a) => (
            <div key={a.activity_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span>{aIcon[a.action] ?? "•"}</span>
                <span className="text-gray-700 dark:text-gray-300">{a.developer_id}</span>
              </div>
              <span className="text-gray-400">{a.action.replace(/_/g, " ")}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
