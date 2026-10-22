"use client";

import { useState } from "react";

interface Notification { type: string; title: string; message: string; read: boolean; created_at: string; }

interface NotificationBellProps { notifications: Notification[]; onMarkAllRead: () => void; }

export function NotificationBell({ notifications, onMarkAllRead }: NotificationBellProps) {
  const [open, setOpen] = useState(false);
  const unread = notifications.filter(n => !n.read).length;

  return (
    <div className="relative">
      <button onClick={() => setOpen(!open)} className="relative rounded-full p-2 hover:bg-gray-100 dark:hover:bg-gray-700" aria-label="Notifications">
        🔔
        {unread > 0 && (
          <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-xs text-white">
            {unread > 9 ? "9+" : unread}
          </span>
        )}
      </button>
      {open && (
        <div className="absolute right-0 top-10 z-50 w-80 rounded-lg border bg-white shadow-lg dark:border-gray-700 dark:bg-gray-800">
          <div className="flex items-center justify-between border-b px-4 py-2 dark:border-gray-700">
            <span className="text-sm font-semibold">Notifications</span>
            {unread > 0 && <button onClick={onMarkAllRead} className="text-xs text-blue-600">Mark all read</button>}
          </div>
          <div className="max-h-64 overflow-y-auto">
            {notifications.length === 0 ? (
              <p className="p-4 text-center text-sm text-gray-400">No notifications</p>
            ) : notifications.map((n, i) => (
              <div key={i} className={`border-b px-4 py-3 text-sm dark:border-gray-700 ${n.read ? "opacity-60" : ""}`}>
                <p className="font-medium">{n.title}</p>
                <p className="text-gray-500">{n.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
