"use client";

interface NotifInfo { notification_id: string; version: string; channel: string; recipient_count: number; delivered: number; failed: number; }
interface Props { notifications: NotifInfo[]; appName: string; }

const chIcon: Record<string, string> = { email: "📧", slack: "💬", webhook: "🔗" };

export default function APIChangelogNotificationCard({ notifications, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📢 Changelog Notifications</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{notifications.length} sent</span>
      </div>
      {notifications.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No notifications sent</p>
      ) : (
        <div className="space-y-1">
          {notifications.map((n) => (
            <div key={n.notification_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span>{chIcon[n.channel] ?? "📨"}</span>
                <span className="text-gray-700 dark:text-gray-300">{n.version}</span>
              </div>
              <span className="text-gray-400">{n.delivered}/{n.recipient_count} delivered</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
