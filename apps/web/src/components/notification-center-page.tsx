"use client";

import { useState } from "react";

interface Notification { id: string; title: string; body: string; icon: string;
  category: string; read: boolean; timestamp: string; }
interface Category { id: string; label: string; count: number; unread: number; }
interface NotificationCenterPageProps { notifications: Notification[]; unread: number;
  categories: Category[]; onMarkRead: (id: string) => void; onMarkAllRead: () => void; }

export function NotificationCenterPage({ notifications, unread, categories,
  onMarkRead, onMarkAllRead }: NotificationCenterPageProps) {
  const [filter, setFilter] = useState("all");
  const filtered = filter === "all" ? notifications : notifications.filter(n => n.category === filter);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔔 Notifications</h2>
        <div className="flex items-center gap-2">
          {unread > 0 && <span className="rounded-full bg-blue-600 px-2.5 py-0.5 text-xs text-white">{unread} unread</span>}
          {unread > 0 && <button onClick={onMarkAllRead} className="text-xs text-blue-600 hover:underline">Mark all read</button>}
        </div>
      </div>
      <div className="flex gap-1">
        <button onClick={() => setFilter("all")}
          className={`rounded px-2 py-0.5 text-xs ${filter === "all" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>All</button>
        {categories.map(c => (
          <button key={c.id} onClick={() => setFilter(c.id)}
            className={`rounded px-2 py-0.5 text-xs ${filter === c.id ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>
            {c.label} {c.unread > 0 && <span className="ml-0.5 text-xs">({c.unread})</span>}
          </button>
        ))}
      </div>
      <div className="divide-y rounded-xl border dark:divide-gray-700 dark:border-gray-700">
        {filtered.map(n => (
          <div key={n.id} onClick={() => !n.read && onMarkRead(n.id)}
            className={`flex items-start gap-3 px-4 py-3 cursor-pointer ${n.read ? "opacity-50" : "bg-blue-50/50 dark:bg-blue-900/5"}`}>
            <span className="text-lg mt-0.5">{n.icon}</span>
            <div className="flex-1">
              <p className="text-sm font-medium">{n.title}</p>
              {n.body && <p className="text-xs text-gray-500 mt-0.5">{n.body}</p>}
              <time className="text-xs text-gray-400">{n.timestamp}</time>
            </div>
            {!n.read && <span className="h-2 w-2 rounded-full bg-blue-600 mt-2 shrink-0" />}
          </div>
        ))}
      </div>
    </div>
  );
}
