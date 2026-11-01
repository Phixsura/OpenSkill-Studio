"use client";

interface Channel { id: string; type: string; destination: string; verified: boolean; enabled: boolean; }
interface Props { channels: Channel[]; consumerId: string; unreadCount: number; appName: string; }

const typeIcons: Record<string, string> = { email: "📧", webhook: "🔗", slack: "💬", sms: "📱", in_app: "🔔" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerNotificationChannelCard({ channels, consumerId, unreadCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📬 Notification Channels</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
        </div>
        {unreadCount > 0 && <span className="rounded-full bg-red-500 px-2 py-0.5 text-[10px] font-bold text-white">{unreadCount}</span>}
      </div>
      {channels.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No channels configured</p>
      ) : (
        <div className="space-y-1">
          {channels.map((c) => (
            <div key={c.id} className={`flex items-center justify-between rounded bg-gray-50 px-2 py-1.5 text-[11px] dark:bg-gray-800 ${!c.enabled ? "opacity-50" : ""}`}>
              <div className="flex items-center gap-1">
                <span>{typeIcons[c.type] ?? "📌"}</span>
                <span className="text-gray-700 dark:text-gray-300">{c.destination}</span>
              </div>
              <div className="flex gap-1">
                {c.verified ? <span className="text-green-500 text-[10px]">✓</span> : <span className="text-amber-500 text-[10px]">unverified</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
