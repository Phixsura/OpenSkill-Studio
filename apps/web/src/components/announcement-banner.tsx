"use client";

interface Announcement { id: string; title: string; body: string; variant: string;
  link: string; dismissible: boolean; }
interface AnnouncementBannerProps { announcements: Announcement[];
  onDismiss: (id: string) => void; }

const VARIANT_STYLE: Record<string, string> = {
  info: "bg-blue-50 border-blue-200 text-blue-700 dark:bg-blue-900/20 dark:border-blue-800 dark:text-blue-400",
  success: "bg-green-50 border-green-200 text-green-700 dark:bg-green-900/20 dark:border-green-800",
  warning: "bg-yellow-50 border-yellow-200 text-yellow-700 dark:bg-yellow-900/20 dark:border-yellow-800",
  danger: "bg-red-50 border-red-200 text-red-700 dark:bg-red-900/20 dark:border-red-800",
};

export function AnnouncementBanner({ announcements, onDismiss }: AnnouncementBannerProps) {
  if (!announcements.length) return null;
  return (
    <div className="space-y-2">
      {announcements.map(a => (
        <div key={a.id} className={`rounded-lg border p-3 flex items-start justify-between ${VARIANT_STYLE[a.variant] || VARIANT_STYLE.info}`}>
          <div>
            <p className="text-sm font-medium">{a.title}</p>
            {a.body && <p className="text-xs mt-0.5 opacity-80">{a.body}</p>}
          </div>
          {a.dismissible && (
            <button onClick={() => onDismiss(a.id)} className="text-xs opacity-60 hover:opacity-100 ml-2">✕</button>
          )}
        </div>
      ))}
    </div>
  );
}
