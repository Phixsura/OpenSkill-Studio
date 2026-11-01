"use client";

interface Announcement { id: string; title: string; body: string; type: "info" | "warning" | "feature" | "maintenance"; dismissible: boolean; }

const typeConfig: Record<string, { bg: string; icon: string }> = {
  info: { bg: "bg-blue-50 dark:bg-blue-900/10 border-blue-300", icon: "ℹ️" },
  warning: { bg: "bg-yellow-50 dark:bg-yellow-900/10 border-yellow-300", icon: "⚠️" },
  feature: { bg: "bg-green-50 dark:bg-green-900/10 border-green-300", icon: "✨" },
  maintenance: { bg: "bg-orange-50 dark:bg-orange-900/10 border-orange-300", icon: "🔧" },
};

export function AnnouncementBanner({ announcements, onDismiss }: { announcements: Announcement[]; onDismiss?: (id: string) => void }) {
  if (!announcements.length) return null;
  return (
    <div className="space-y-2">
      {announcements.map((a) => {
        const cfg = typeConfig[a.type] || typeConfig.info;
        return (
          <div key={a.id} className={`rounded-lg border-l-4 p-3 ${cfg.bg} flex items-start justify-between`}>
            <div className="flex gap-2">
              <span>{cfg.icon}</span>
              <div>
                <span className="font-semibold text-sm">{a.title}</span>
                <p className="text-xs text-gray-600 dark:text-gray-400">{a.body}</p>
              </div>
            </div>
            {a.dismissible && (
              <button onClick={() => onDismiss?.(a.id)} className="text-xs text-gray-400 hover:text-gray-600">✕</button>
            )}
          </div>
        );
      })}
    </div>
  );
}
