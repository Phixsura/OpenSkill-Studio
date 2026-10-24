"use client";

interface Notification { id: string; title: string; body: string; category: string; read: boolean; }
interface NotificationBellProps { notifications: Notification[]; unreadCount: number;
  onMarkRead: (id: string) => void; onMarkAllRead: () => void; }

const CAT_ICON: Record<string, string> = {
  deploy: "🚀", onboarding: "👋", alert: "🚨", social: "👥", info: "ℹ️",
};

export function NotificationBell({ notifications, unreadCount, onMarkRead, onMarkAllRead }: NotificationBellProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden w-80">
      <div className="flex items-center justify-between p-3 border-b dark:border-gray-700">
        <div className="flex items-center gap-2">
          <span className="text-lg">🔔</span>
          <span className="text-sm font-semibold">Notifications</span>
          {unreadCount > 0 && (
            <span className="text-xs px-1.5 py-0.5 rounded-full bg-red-500 text-white font-bold">{unreadCount}</span>
          )}
        </div>
        {unreadCount > 0 && (
          <button onClick={onMarkAllRead} className="text-xs text-blue-600 hover:text-blue-700">Mark all read</button>
        )}
      </div>
      <div className="max-h-64 overflow-y-auto divide-y dark:divide-gray-700">
        {notifications.map(n => (
          <button key={n.id} onClick={() => onMarkRead(n.id)}
            className={`w-full text-left px-3 py-2.5 ${n.read ? "opacity-60" : "bg-blue-50/50 dark:bg-blue-900/10"}`}>
            <div className="flex items-start gap-2">
              <span>{CAT_ICON[n.category] || "📌"}</span>
              <div>
                <p className={`text-sm ${n.read ? "" : "font-medium"}`}>{n.title}</p>
                {n.body && <p className="text-xs text-gray-400 line-clamp-1">{n.body}</p>}
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
