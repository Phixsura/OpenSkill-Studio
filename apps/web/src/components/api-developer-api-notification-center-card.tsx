"use client";

interface NotifInfo { notification_id: string; title: string; category: string; read: boolean; }
interface Props { notifications: NotifInfo[]; unreadCount: number; appName: string; }

const catIcon: Record<string, string> = { system: "⚙️", changelog: "📋", incident: "🚨", security: "🛡️", billing: "💰" };

export default function APIDeveloperAPINotificationCenterCard({ notifications, unreadCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔔 Notification Center</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {unreadCount > 0 && <span className="rounded-full bg-red-500 px-2 py-0.5 text-[10px] font-bold text-white">{unreadCount}</span>}
      </div>
      {notifications.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No notifications</p>
      ) : (
        <div className="space-y-1">
          {notifications.map((n) => (
            <div key={n.notification_id} className={`flex items-center gap-2 text-[11px] ${n.read ? "opacity-50" : ""}`}>
              <span>{catIcon[n.category] ?? "📨"}</span>
              {!n.read && <span className="h-1.5 w-1.5 rounded-full bg-blue-500" />}
              <span className="text-gray-700 dark:text-gray-300">{n.title}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
