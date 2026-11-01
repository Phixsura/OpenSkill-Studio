"use client";

interface Notification {
  notificationId: string;
  title: string;
  body: string;
  channels: string[];
  read: boolean;
  timestamp: string;
}

export function NotificationHubPanel({
  notifications, unreadCount, onMarkRead, onMarkAllRead,
}: {
  notifications: Notification[]; unreadCount: number;
  onMarkRead?: (id: string) => void; onMarkAllRead?: () => void;
}) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-bold">🔔 Notifications</h2>
          {unreadCount > 0 && <span className="text-xs bg-red-600 text-white px-2 py-0.5 rounded-full">{unreadCount}</span>}
        </div>
        <button onClick={onMarkAllRead} className="text-xs text-blue-600">Mark all read</button>
      </div>
      <div className="space-y-1">
        {notifications.map((n) => (
          <div key={n.notificationId} onClick={() => !n.read && onMarkRead?.(n.notificationId)}
            className={`rounded-lg border dark:border-gray-700 p-3 cursor-pointer ${n.read ? "opacity-50" : "border-l-4 border-l-blue-500"}`}>
            <div className="flex justify-between">
              <span className="font-semibold text-sm">{n.title}</span>
              <span className="text-xs text-gray-400">{n.timestamp}</span>
            </div>
            <p className="text-xs text-gray-500 mt-0.5">{n.body}</p>
            <div className="flex gap-1 mt-1">
              {n.channels.map((c) => <span key={c} className="text-[10px] bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded">{c}</span>)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
