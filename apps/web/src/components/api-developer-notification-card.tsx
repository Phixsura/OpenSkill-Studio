"use client";

interface NotifInfo { notification_id: string; title: string; channel: string; read: boolean; }
interface Props { notifications: NotifInfo[]; unreadCount: number; appName: string; }

export default function APIDeveloperNotificationCard({ notifications, unreadCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔔 Notifications</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{notifications.length} total</span>
          {unreadCount > 0 && <p className="text-[10px] text-blue-600">{unreadCount} unread</p>}
        </div>
      </div>
      {notifications.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No notifications</p>
      ) : (
        <div className="space-y-1">
          {notifications.map((n) => (
            <div key={n.notification_id} className={`flex items-center justify-between text-[11px] ${n.read ? "opacity-50" : ""}`}>
              <div className="flex items-center gap-1.5">
                {!n.read && <span className="h-1.5 w-1.5 rounded-full bg-blue-500" />}
                <span className="text-gray-700 dark:text-gray-300">{n.title}</span>
              </div>
              <span className="text-gray-400">{n.channel}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
