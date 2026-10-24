"use client";

import { useState } from "react";

interface Notification { id: string; title: string; body: string; icon: string; read: boolean; timestamp: string; }
interface Tab { id: string; label: string; count: number; unread: number; }
interface NotificationsPageProps { tabs: Tab[]; notificationsByTab: Record<string, Notification[]>;
  unread: number; onMarkRead: (id: string) => void; }

export function NotificationsPage({ tabs, notificationsByTab, unread, onMarkRead }: NotificationsPageProps) {
  const [activeTab, setActiveTab] = useState(tabs[0]?.id ?? "");
  const items = notificationsByTab[activeTab] ?? [];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔔 Notifications</h2>
        {unread > 0 && <span className="rounded-full bg-blue-600 px-2.5 py-0.5 text-xs text-white">{unread} unread</span>}
      </div>
      <div className="flex gap-1 border-b dark:border-gray-700">
        {tabs.map(t => (
          <button key={t.id} onClick={() => setActiveTab(t.id)}
            className={`px-3 py-2 text-sm ${activeTab === t.id ? "border-b-2 border-blue-600 font-medium" : "text-gray-400"}`}>
            {t.label} {t.unread > 0 && <span className="ml-1 rounded-full bg-red-500 px-1.5 py-0.5 text-xs text-white">{t.unread}</span>}
          </button>
        ))}
      </div>
      <div className="space-y-1">
        {items.map(n => (
          <div key={n.id} onClick={() => !n.read && onMarkRead(n.id)}
            className={`flex items-start gap-3 rounded-lg px-4 py-3 cursor-pointer ${n.read ? "opacity-60" : "bg-blue-50 dark:bg-blue-900/10"}`}>
            <span className="text-lg mt-0.5">{n.icon}</span>
            <div className="flex-1">
              <p className="text-sm font-medium">{n.title}</p>
              {n.body && <p className="text-xs text-gray-500 mt-0.5">{n.body}</p>}
              <time className="text-xs text-gray-400">{n.timestamp}</time>
            </div>
            {!n.read && <span className="h-2 w-2 rounded-full bg-blue-600 mt-2" />}
          </div>
        ))}
      </div>
    </div>
  );
}
