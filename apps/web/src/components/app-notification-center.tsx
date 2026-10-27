"use client";

import { useState } from "react";

interface AppNotification {
  notification_id: string;
  app_name: string;
  app_id: string;
  title: string;
  body: string;
  priority: "info" | "warning" | "action_required";
  action_url: string | null;
  read: boolean;
  created_at: string;
}

interface AppNotificationCenterProps {
  notifications: AppNotification[];
  unreadCount: number;
  onMarkRead: (id: string) => void;
  onDismiss: (id: string) => void;
  onMarkAllRead: () => void;
  onAction: (url: string) => void;
}

const PRIORITY_STYLES: Record<string, { dot: string; bg: string; border: string }> = {
  info: { dot: "bg-blue-500", bg: "", border: "" },
  warning: {
    dot: "bg-yellow-500",
    bg: "bg-yellow-50 dark:bg-yellow-900/5",
    border: "border-l-2 border-l-yellow-500",
  },
  action_required: {
    dot: "bg-red-500",
    bg: "bg-red-50 dark:bg-red-900/5",
    border: "border-l-2 border-l-red-500",
  },
};

function timeAgo(iso: string): string {
  try {
    const diff = Date.now() - new Date(iso).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return "Just now";
    if (mins < 60) return `${mins}m ago`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  } catch {
    return iso;
  }
}

function NotificationItem({
  notif,
  onMarkRead,
  onDismiss,
  onAction,
}: {
  notif: AppNotification;
  onMarkRead: (id: string) => void;
  onDismiss: (id: string) => void;
  onAction: (url: string) => void;
}) {
  const style = PRIORITY_STYLES[notif.priority] ?? PRIORITY_STYLES.info;

  return (
    <div
      className={`flex gap-3 px-4 py-3 ${style.bg} ${style.border} ${!notif.read ? "bg-blue-50/50 dark:bg-blue-900/5" : ""}`}
    >
      <span
        className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${style.dot} ${notif.read ? "opacity-30" : ""}`}
      />
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <span className={`text-sm ${notif.read ? "text-gray-500" : "font-medium"}`}>
            {notif.title}
          </span>
          <span className="text-[10px] text-gray-400">{notif.app_name}</span>
          <span className="ml-auto shrink-0 text-[10px] text-gray-400">
            {timeAgo(notif.created_at)}
          </span>
        </div>
        <p className="mt-0.5 line-clamp-2 text-xs text-gray-500">{notif.body}</p>
        <div className="mt-1.5 flex gap-2">
          {notif.action_url && (
            <button
              onClick={() => onAction(notif.action_url!)}
              className="text-[10px] font-medium text-blue-600 hover:underline dark:text-blue-400"
            >
              View Details
            </button>
          )}
          {!notif.read && (
            <button
              onClick={() => onMarkRead(notif.notification_id)}
              className="text-[10px] text-gray-400 hover:text-gray-600"
            >
              Mark read
            </button>
          )}
          <button
            onClick={() => onDismiss(notif.notification_id)}
            className="text-[10px] text-gray-400 hover:text-red-500"
          >
            Dismiss
          </button>
        </div>
      </div>
    </div>
  );
}

export function AppNotificationCenter({
  notifications,
  unreadCount,
  onMarkRead,
  onDismiss,
  onMarkAllRead,
  onAction,
}: AppNotificationCenterProps) {
  const [filter, setFilter] = useState<"all" | "unread">("all");
  const filtered = filter === "unread" ? notifications.filter((n) => !n.read) : notifications;

  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3 dark:border-gray-700">
        <div className="flex items-center gap-2">
          <h3 className="font-semibold">Notifications</h3>
          {unreadCount > 0 && (
            <span className="flex h-5 min-w-5 items-center justify-center rounded-full bg-red-500 px-1.5 text-[10px] font-bold text-white">
              {unreadCount}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <div className="flex gap-0.5 rounded bg-gray-100 p-0.5 dark:bg-gray-800">
            <button
              onClick={() => setFilter("all")}
              className={`rounded px-2 py-0.5 text-[10px] ${filter === "all" ? "bg-white shadow dark:bg-gray-700" : "text-gray-500"}`}
            >
              All
            </button>
            <button
              onClick={() => setFilter("unread")}
              className={`rounded px-2 py-0.5 text-[10px] ${filter === "unread" ? "bg-white shadow dark:bg-gray-700" : "text-gray-500"}`}
            >
              Unread
            </button>
          </div>
          {unreadCount > 0 && (
            <button
              onClick={onMarkAllRead}
              className="text-[10px] text-blue-600 hover:underline dark:text-blue-400"
            >
              Mark all read
            </button>
          )}
        </div>
      </div>

      {/* List */}
      {filtered.length === 0 ? (
        <div className="py-8 text-center">
          <span className="text-3xl">🔔</span>
          <p className="mt-2 text-sm text-gray-500">
            {filter === "unread" ? "No unread notifications" : "No notifications"}
          </p>
        </div>
      ) : (
        <div className="divide-y divide-gray-100 dark:divide-gray-800">
          {filtered.map((n) => (
            <NotificationItem
              key={n.notification_id}
              notif={n}
              onMarkRead={onMarkRead}
              onDismiss={onDismiss}
              onAction={onAction}
            />
          ))}
        </div>
      )}
    </div>
  );
}
