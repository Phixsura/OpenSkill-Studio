"use client";

interface DigestInfo { digest_id: string; period: string; notification_count: number; categories: Record<string, number>; }
interface Props { digests: DigestInfo[]; unreadCount: number; consumerId: string; appName: string; }

const catEmoji: Record<string, string> = { alert: "🚨", changelog: "📰", billing: "💵", security: "🔒", usage: "📊", system: "⚙️" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiNotificationDigestCard({ digests, unreadCount, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📬 Notification Digest</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
        </div>
        {unreadCount > 0 && <span className="rounded-full bg-blue-100 px-2 py-0.5 text-[10px] font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">{unreadCount} pending</span>}
      </div>
      {digests.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No digests</p>
      ) : (
        <div className="space-y-1.5">
          {digests.map((d) => (
            <div key={d.digest_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{d.period}</span>
                <span className="text-gray-400">{d.notification_count} items</span>
              </div>
              <div className="flex gap-2 text-[10px] text-gray-400">
                {Object.entries(d.categories).map(([cat, count]) => <span key={cat}>{catEmoji[cat] ?? ""} {count}</span>)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
