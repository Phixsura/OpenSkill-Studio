"use client";

interface Announcement { announcement_id: string; title: string; content: string;
  priority: string; published_at: string; }
interface PlatformAnnouncementListProps { announcements: Announcement[];
  onDismiss: (id: string) => void; }

const prioStyle: Record<string, { bg: string; icon: string }> = {
  urgent: { bg: "border-red-300 bg-red-50 dark:border-red-700 dark:bg-red-900/10", icon: "🚨" },
  high: { bg: "border-orange-300 bg-orange-50 dark:border-orange-700 dark:bg-orange-900/10", icon: "⚠️" },
  normal: { bg: "border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-900/10", icon: "📢" },
  low: { bg: "border-gray-200 dark:border-gray-700", icon: "ℹ️" },
};

export function PlatformAnnouncementList({ announcements, onDismiss }: PlatformAnnouncementListProps) {
  if (announcements.length === 0) return null;
  return (
    <div className="space-y-2">
      {announcements.map(a => {
        const p = prioStyle[a.priority] ?? prioStyle.normal;
        return (
          <div key={a.announcement_id} className={`flex items-start justify-between rounded-lg border p-3 ${p.bg}`}>
            <div className="flex gap-2">
              <span>{p.icon}</span>
              <div>
                <p className="text-sm font-semibold">{a.title}</p>
                <p className="text-xs text-gray-500">{a.content}</p>
              </div>
            </div>
            <button onClick={() => onDismiss(a.announcement_id)} className="text-xs text-gray-400">✕</button>
          </div>
        );
      })}
    </div>
  );
}
