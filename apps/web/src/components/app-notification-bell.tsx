"use client";

interface AppNotificationBellProps {
  count: number;
  onClick?: () => void;
}

export function AppNotificationBell({ count, onClick }: AppNotificationBellProps) {
  return (
    <button onClick={onClick} className="relative rounded-full p-2 hover:bg-gray-100 dark:hover:bg-gray-800" aria-label="Notifications">
      <span className="text-xl">🔔</span>
      {count > 0 && (
        <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-xs text-white">
          {count > 99 ? "99+" : count}
        </span>
      )}
    </button>
  );
}
