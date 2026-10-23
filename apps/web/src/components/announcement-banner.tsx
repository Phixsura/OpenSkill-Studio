"use client";

interface AnnouncementBannerProps { title: string; body: string; type: string; onDismiss: () => void; }

const TYPE_STYLES: Record<string, string> = {
  info: "bg-blue-50 text-blue-800 border-blue-200 dark:bg-blue-900/20 dark:text-blue-200 dark:border-blue-800",
  warning: "bg-yellow-50 text-yellow-800 border-yellow-200 dark:bg-yellow-900/20 dark:text-yellow-200",
  critical: "bg-red-50 text-red-800 border-red-200 dark:bg-red-900/20 dark:text-red-200",
  feature: "bg-purple-50 text-purple-800 border-purple-200 dark:bg-purple-900/20 dark:text-purple-200",
};

export function AnnouncementBanner({ title, body, type, onDismiss }: AnnouncementBannerProps) {
  return (
    <div className={`rounded-lg border p-4 ${TYPE_STYLES[type] || TYPE_STYLES.info}`}>
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-sm font-semibold">{title}</h3>
          <p className="mt-1 text-xs opacity-80">{body}</p>
        </div>
        <button onClick={onDismiss} className="text-xs opacity-60 hover:opacity-100">✕</button>
      </div>
    </div>
  );
}
