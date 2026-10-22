"use client";

interface Notification { title: string; message: string; type: string; read: boolean; createdAt: string; }
interface NotificationCenterProps { notifications: Notification[]; unreadCount: number; onMarkRead: () => void; }

const TYPE_ICONS: Record<string, string> = { success: "✅", error: "❌", warning: "⚠️", info: "ℹ️" };

export function NotificationCenter({ notifications, unreadCount, onMarkRead }: NotificationCenterProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="mb-3 flex items-center justify-between">
        <h4 className="font-semibold">🔔 Notifications {unreadCount > 0 && <span className="ml-1 rounded-full bg-red-500 px-1.5 text-xs text-white">{unreadCount}</span>}</h4>
        {unreadCount > 0 && <button onClick={onMarkRead} className="text-xs text-blue-600">Mark all read</button>}
      </div>
      {notifications.length === 0 ? <p className="text-sm text-gray-400">No notifications</p> : (
        <div className="space-y-2">{notifications.map((n, i) => (
          <div key={i} className={`rounded border p-2 text-sm ${n.read ? "border-gray-100 opacity-60" : "border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-900/20"}`}>
            <span>{TYPE_ICONS[n.type] ?? "•"}</span> <span className="font-medium">{n.title}</span>
            <p className="text-xs text-gray-500">{n.message}</p>
          </div>
        ))}</div>
      )}
    </div>
  );
}
