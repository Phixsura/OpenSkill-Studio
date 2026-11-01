"use client";

interface DeliveryInfo {
  version: string;
  channel: string;
  recipient: string;
  success: boolean;
}

interface ChangelogNotifyCardProps {
  deliveries: DeliveryInfo[];
  totalDeliveries: number;
  appName: string;
}

const CHANNEL_ICONS: Record<string, string> = { email: "✉️", slack: "💬", webhook: "🔗" };

export default function ChangelogNotifyCard({
  deliveries,
  totalDeliveries,
  appName,
}: ChangelogNotifyCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Release Notifications
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{totalDeliveries} sent</span>
      </div>

      {deliveries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No notifications sent</p>
      ) : (
        <div className="space-y-1">
          {deliveries.map((d, i) => (
            <div
              key={i}
              className="flex items-center justify-between rounded px-2 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-800/50"
            >
              <div className="flex items-center gap-2">
                <span>{CHANNEL_ICONS[d.channel] ?? "📨"}</span>
                <span className="text-xs text-gray-700 dark:text-gray-300">{d.recipient}</span>
              </div>
              <div className="flex items-center gap-2 text-[11px] text-gray-400">
                <span className="font-mono">v{d.version}</span>
                <span className={d.success ? "text-green-500" : "text-red-500"}>
                  {d.success ? "✓" : "✕"}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
