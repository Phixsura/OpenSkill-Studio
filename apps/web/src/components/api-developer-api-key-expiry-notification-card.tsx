"use client";

interface NotifInfo { notification_id: string; key_id: string; developer_id: string; days_until_expiry: number; sent: boolean; }
interface Props { notifications: NotifInfo[]; appName: string; }

export default function APIDeveloperAPIKeyExpiryNotificationCard({ notifications, appName }: Props) {
  const urgent = notifications.filter((n) => n.days_until_expiry <= 7 && !n.sent).length;
  const pending = notifications.filter((n) => !n.sent).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⏰ Key Expiry Alerts</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{pending} pending</span>
          {urgent > 0 && <p className="text-[10px] text-red-500">{urgent} urgent</p>}
        </div>
      </div>
      {notifications.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No expiry alerts</p>
      ) : (
        <div className="space-y-1">
          {notifications.filter((n) => !n.sent).map((n) => (
            <div key={n.notification_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{n.developer_id} — {n.key_id}</span>
              <span className={`font-medium ${n.days_until_expiry <= 7 ? "text-red-500" : "text-yellow-600"}`}>{n.days_until_expiry}d</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
