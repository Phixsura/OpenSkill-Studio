"use client";
import { useState } from "react";

interface Notif { notifId: string; title: string; body: string; category: string; read: boolean; actionUrl: string; }

const catIcons: Record<string, string> = { install: "📥", update: "🔄", review: "⭐", security: "🔒", system: "⚙️", revenue: "💰" };

export function NotificationBell({ notifications, unreadCount, onMarkRead, onMarkAllRead }: {
  notifications: Notif[]; unreadCount: number;
  onMarkRead?: (id: string) => void; onMarkAllRead?: () => void;
}) {
  const [open, setOpen] = useState(false);

  return (
    <div className="relative">
      <button onClick={() => setOpen(!open)} className="relative p-2">
        <span className="text-xl">🔔</span>
        {unreadCount > 0 && (
          <span className="absolute -top-0.5 -right-0.5 bg-red-500 text-white text-[10px] w-4 h-4 rounded-full flex items-center justify-center">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>
      {open && (
        <div className="absolute right-0 top-10 w-72 bg-white dark:bg-gray-900 border dark:border-gray-700 rounded-xl shadow-lg z-50 max-h-80 overflow-y-auto">
          <div className="flex justify-between items-center p-3 border-b dark:border-gray-700">
            <span className="font-bold text-sm">Notifications</span>
            {unreadCount > 0 && <button onClick={onMarkAllRead} className="text-xs text-blue-500">Mark all read</button>}
          </div>
          {notifications.length === 0 ? (
            <div className="p-4 text-center text-gray-400 text-sm">No notifications</div>
          ) : notifications.map(n => (
            <button key={n.notifId} onClick={() => onMarkRead?.(n.notifId)}
              className={`w-full text-left p-3 border-b dark:border-gray-700 text-xs ${!n.read ? "bg-blue-50 dark:bg-blue-900/10" : ""}`}>
              <div className="flex items-start gap-2">
                <span>{catIcons[n.category] || "📌"}</span>
                <div>
                  <span className={`font-medium block ${!n.read ? "" : "text-gray-400"}`}>{n.title}</span>
                  <span className="text-gray-500">{n.body}</span>
                </div>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
