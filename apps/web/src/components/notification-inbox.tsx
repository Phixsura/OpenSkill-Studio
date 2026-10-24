"use client";

interface Notification { notification_id: string; title: string; message: string;
  type: string; icon: string; read: boolean; created_at: string; action_url?: string; }
interface NotificationInboxProps { notifications: Notification[]; unreadCount: number;
  onRead: (id: string) => void; onReadAll: () => void; }

export function NotificationInbox({ notifications, unreadCount, onRead, onReadAll }: NotificationInboxProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-semibold">Notifications</h2>
          {unreadCount > 0 && (
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-xs text-white">{unreadCount}</span>
          )}
        </div>
        {unreadCount > 0 && (
          <button onClick={onReadAll} className="text-xs text-blue-500">Mark all read</button>
        )}
      </div>
      <div className="space-y-1">
        {notifications.map(n => (
          <button key={n.notification_id} onClick={() => onRead(n.notification_id)}
            className={`flex w-full items-start gap-3 rounded-lg border p-3 text-left ${!n.read ? "bg-blue-50/50 dark:bg-blue-900/5" : ""} dark:border-gray-700`}>
            <span className="text-lg">{n.icon}</span>
            <div className="flex-1">
              <p className={`text-sm ${!n.read ? "font-semibold" : ""}`}>{n.title}</p>
              <p className="text-xs text-gray-400">{n.message}</p>
              <p className="mt-0.5 text-[10px] text-gray-300">{new Date(n.created_at).toLocaleString()}</p>
            </div>
            {!n.read && <span className="mt-1 h-2 w-2 rounded-full bg-blue-500" />}
          </button>
        ))}
        {notifications.length === 0 && <p className="py-4 text-center text-sm text-gray-400">No notifications</p>}
      </div>
    </div>
  );
}
