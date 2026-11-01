"use client";

interface Notification { id: number; title: string; body: string;
  category: string; priority: string; read: boolean; }
interface NotificationCenterProps { notifications: Notification[];
  unread: number; onMarkRead: (id: number) => void; onMarkAllRead: () => void; }

const CAT_ICONS: Record<string, string> = {
  deploy: "🚀", alert: "🚨", system: "⚙️", info: "ℹ️", billing: "💳",
};

export function NotificationCenter({ notifications, unread, onMarkRead, onMarkAllRead }: NotificationCenterProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔔 Notifications</h3>
        <div className="flex gap-2">
          {unread > 0 && <span className="px-2 py-0.5 text-[10px] bg-red-500 text-white rounded-full">{unread}</span>}
          <button onClick={onMarkAllRead} className="text-xs text-blue-500 hover:underline">Mark all read</button>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700 max-h-64 overflow-y-auto">
        {notifications.map(n => (
          <div key={n.id} onClick={() => !n.read && onMarkRead(n.id)}
            className={`px-4 py-2.5 cursor-pointer ${!n.read ? "bg-blue-50/50 dark:bg-blue-900/5" : ""}`}>
            <div className="flex items-center gap-2">
              <span>{CAT_ICONS[n.category] ?? "📨"}</span>
              <span className={`text-sm ${!n.read ? "font-medium" : "text-gray-500"}`}>{n.title}</span>
              {n.priority === "high" && <span className="text-[10px] text-red-500">urgent</span>}
            </div>
            <div className="text-xs text-gray-400 mt-0.5 pl-6">{n.body}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
