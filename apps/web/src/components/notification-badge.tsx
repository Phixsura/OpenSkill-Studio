"use client";

interface NotificationBadgeProps { unread: number; display: string; hasUrgent: boolean;
  onClick: () => void; }

export function NotificationBadge({ unread, display, hasUrgent, onClick }: NotificationBadgeProps) {
  return (
    <button onClick={onClick} className="relative p-1">
      <span className="text-xl">🔔</span>
      {unread > 0 && (
        <span className={`absolute -top-1 -right-1 flex h-5 min-w-[20px] items-center justify-center rounded-full px-1 text-xs font-bold text-white ${hasUrgent ? "bg-red-600 animate-pulse" : "bg-blue-600"}`}>
          {display}
        </span>
      )}
    </button>
  );
}
