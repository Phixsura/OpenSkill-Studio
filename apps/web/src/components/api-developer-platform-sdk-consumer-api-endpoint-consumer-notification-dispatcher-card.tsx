"use client";

interface NotificationItem { id: string; title: string; message: string; severity: string; read: boolean; dispatchedAt: string; channels: string[]; }
interface Props { notifications: NotificationItem[]; unreadCount: number; channels: string[]; consumerId: string; appName: string; }

const sevColors: Record<string, string> = { info: "border-l-blue-500", warning: "border-l-amber-500", critical: "border-l-red-500" };

export default function APIDeveloperPlatformSDKConsumerApiEndpointConsumerNotificationDispatcherCard({ notifications, unreadCount, channels, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔔 Notifications</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {channels.join(", ")}</p>
        </div>
        {unreadCount > 0 && <span className="rounded-full bg-red-500 px-2 py-0.5 text-[10px] font-bold text-white">{unreadCount}</span>}
      </div>
      {notifications.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No notifications</p>
      ) : (
        <div className="space-y-1.5">
          {notifications.slice(0, 6).map((n) => (
            <div key={n.id} className={`rounded border-l-4 bg-gray-50 px-2 py-1.5 dark:bg-gray-800 ${sevColors[n.severity] ?? ""} ${n.read ? "opacity-60" : ""}`}>
              <div className="flex justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{n.title}</span>
                <span className="text-[9px] text-gray-400">{n.dispatchedAt}</span>
              </div>
              <div className="text-[10px] text-gray-500">{n.message}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
