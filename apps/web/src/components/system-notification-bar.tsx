"use client";

interface SystemNotification { notification_id: string; title: string; message: string;
  severity: string; dismissible: boolean; }
interface SystemNotificationBarProps { notifications: SystemNotification[];
  onDismiss: (id: string) => void; }

const sevStyle: Record<string, { bg: string; icon: string }> = {
  info: { bg: "bg-blue-50 border-blue-200 dark:bg-blue-900/10 dark:border-blue-800", icon: "ℹ️" },
  warning: { bg: "bg-yellow-50 border-yellow-200 dark:bg-yellow-900/10 dark:border-yellow-800", icon: "⚠️" },
  critical: { bg: "bg-red-50 border-red-200 dark:bg-red-900/10 dark:border-red-800", icon: "🚨" },
  maintenance: { bg: "bg-orange-50 border-orange-200 dark:bg-orange-900/10 dark:border-orange-800", icon: "🔧" },
};

export function SystemNotificationBar({ notifications, onDismiss }: SystemNotificationBarProps) {
  if (notifications.length === 0) return null;
  return (
    <div className="space-y-2">
      {notifications.map(n => {
        const s = sevStyle[n.severity] ?? sevStyle.info;
        return (
          <div key={n.notification_id} className={`flex items-start justify-between rounded-lg border p-3 ${s.bg}`}>
            <div className="flex items-start gap-2">
              <span className="text-lg">{s.icon}</span>
              <div>
                <p className="text-sm font-semibold">{n.title}</p>
                <p className="text-xs text-gray-500">{n.message}</p>
              </div>
            </div>
            {n.dismissible && (
              <button onClick={() => onDismiss(n.notification_id)} className="text-xs text-gray-400">✕</button>
            )}
          </div>
        );
      })}
    </div>
  );
}
