"use client";

interface NotificationDotProps { count: number; display: string; visible: boolean;
  color: string; children: React.ReactNode; }

const colorMap: Record<string, string> = {
  red: "bg-red-500", blue: "bg-blue-500", green: "bg-green-500", orange: "bg-orange-500",
};

export function NotificationDot({ count, display, visible, color, children }: NotificationDotProps) {
  return (
    <div className="relative inline-block">
      {children}
      {visible && (
        <span className={`absolute -right-1.5 -top-1.5 flex h-5 min-w-[1.25rem] items-center justify-center rounded-full px-1 text-[10px] font-bold text-white ${colorMap[color] ?? colorMap.red}`}
          aria-label={`${count} notifications`}>
          {display}
        </span>
      )}
    </div>
  );
}
