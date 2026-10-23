"use client";

interface Notification { id: string; title: string; body: string; icon: string; type: string; read: boolean; timestamp: string; }
interface NotificationCenterProps { notifications: Notification[]; onMarkRead: (ids: string[]) => void; }

export function NotificationCenter({ notifications, onMarkRead }: NotificationCenterProps) {
  const unread = notifications.filter(n => !n.read).length;
  return (
    <div className="w-full max-w-md rounded-xl border shadow-lg dark:border-gray-700">
      <div className="flex items-center justify-between border-b px-4 py-3 dark:border-gray-700">
        <h3 className="text-sm font-semibold">Notifications</h3>
        <div className="flex items-center gap-2">
          {unread > 0 && <span className="rounded-full bg-blue-600 px-2 py-0.5 text-xs text-white">{unread}</span>}
          {unread > 0 && (
            <button onClick={() => onMarkRead(notifications.filter(n => !n.read).map(n => n.id))}
              className="text-xs text-blue-600 hover:underline">Mark all read</button>
          )}
        </div>
      </div>
      <div className="max-h-80 overflow-y-auto divide-y dark:divide-gray-700">
        {notifications.map(n => (
          <div key={n.id} className={`flex gap-3 px-4 py-3 ${n.read ? "opacity-60" : "bg-blue-50/50 dark:bg-blue-900/10"}`}>
            <span className="text-lg">{n.icon}</span>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{n.title}</p>
              <p className="text-xs text-gray-500 truncate">{n.body}</p>
              <time className="text-xs text-gray-400">{new Date(n.timestamp).toLocaleDateString()}</time>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
