"use client";

import { useState } from "react";

interface Notification { title: string; icon: string; event_type: string; details: Record<string, unknown>; read: boolean; }
interface NotificationCenterV2Props { notifications: Notification[]; onMarkRead: (index: number) => void; onClearAll: () => void; }

export function NotificationCenterV2({ notifications, onMarkRead, onClearAll }: NotificationCenterV2Props) {
  const [filter, setFilter] = useState<string | null>(null);
  const unread = notifications.filter(n => !n.read).length;
  const filtered = filter ? notifications.filter(n => n.event_type === filter) : notifications;
  const types = [...new Set(notifications.map(n => n.event_type))];

  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between border-b p-3 dark:border-gray-700">
        <h3 className="text-sm font-semibold">Notifications {unread > 0 && <span className="ml-1 rounded-full bg-red-500 px-1.5 py-0.5 text-xs text-white">{unread}</span>}</h3>
        <button onClick={onClearAll} className="text-xs text-gray-400 hover:text-gray-600">Clear all</button>
      </div>
      {types.length > 1 && (
        <div className="flex gap-1 border-b px-3 py-2 dark:border-gray-700">
          <button onClick={() => setFilter(null)} className={`rounded px-2 py-0.5 text-xs ${!filter ? "bg-blue-100 font-semibold" : "text-gray-500"}`}>All</button>
          {types.map(t => <button key={t} onClick={() => setFilter(t)} className={`rounded px-2 py-0.5 text-xs ${filter === t ? "bg-blue-100 font-semibold" : "text-gray-500"}`}>{t}</button>)}
        </div>
      )}
      <ul className="max-h-64 overflow-y-auto">
        {filtered.length === 0 ? <li className="p-4 text-center text-sm text-gray-400">No notifications</li> :
          filtered.map((n, i) => (
            <li key={i} onClick={() => onMarkRead(i)}
              className={`cursor-pointer border-b px-3 py-2 hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800 ${n.read ? "opacity-50" : ""}`}>
              <span className="mr-1">{n.icon}</span>
              <span className="text-sm">{n.title}</span>
            </li>
          ))}
      </ul>
    </div>
  );
}
