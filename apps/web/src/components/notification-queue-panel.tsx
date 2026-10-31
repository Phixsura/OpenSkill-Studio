"use client";

import { useState } from "react";

interface QueueNotification {
  notificationId: string;
  title: string;
  message: string;
  priority: "low" | "normal" | "high" | "urgent";
  category: string;
  read: boolean;
  createdAt: string;
}

const priorityConfig: Record<string, { color: string; icon: string }> = {
  low: { color: "text-gray-400", icon: "○" },
  normal: { color: "text-blue-600", icon: "●" },
  high: { color: "text-orange-500", icon: "◉" },
  urgent: { color: "text-red-600", icon: "🔴" },
};

export function NotificationQueuePanel({
  notifications,
  unreadCount,
  onMarkRead,
  onMarkAllRead,
  onDelete,
}: {
  notifications: QueueNotification[];
  unreadCount: number;
  onMarkRead?: (id: string) => void;
  onMarkAllRead?: () => void;
  onDelete?: (id: string) => void;
}) {
  const [filter, setFilter] = useState<"all" | "unread">("unread");
  const filtered = filter === "unread" ? notifications.filter((n) => !n.read) : notifications;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-bold">🔔 Notifications</h2>
          {unreadCount > 0 && (
            <span className="text-xs bg-red-600 text-white px-2 py-0.5 rounded-full">{unreadCount}</span>
          )}
        </div>
        <button onClick={onMarkAllRead} className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
          Mark All Read
        </button>
      </div>

      <div className="flex gap-1">
        {(["unread", "all"] as const).map((f) => (
          <button key={f} onClick={() => setFilter(f)}
            className={`text-xs px-3 py-1 rounded-lg ${filter === f ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {f === "unread" ? `Unread (${unreadCount})` : "All"}
          </button>
        ))}
      </div>

      <div className="space-y-1">
        {filtered.map((n) => {
          const cfg = priorityConfig[n.priority];
          return (
            <div key={n.notificationId}
              className={`rounded-lg border dark:border-gray-700 p-3 ${n.read ? "opacity-50" : ""}`}>
              <div className="flex items-center justify-between mb-0.5">
                <div className="flex items-center gap-2">
                  <span className={cfg.color}>{cfg.icon}</span>
                  <span className="font-semibold text-sm">{n.title}</span>
                  {n.category && <span className="text-xs bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">{n.category}</span>}
                </div>
                <div className="flex gap-1">
                  {!n.read && (
                    <button onClick={() => onMarkRead?.(n.notificationId)}
                      className="text-xs text-blue-600">Read</button>
                  )}
                  <button onClick={() => onDelete?.(n.notificationId)}
                    className="text-xs text-red-500">✕</button>
                </div>
              </div>
              <p className="text-xs text-gray-500">{n.message}</p>
            </div>
          );
        })}
        {filtered.length === 0 && <span className="text-sm text-gray-500">No notifications</span>}
      </div>
    </div>
  );
}
