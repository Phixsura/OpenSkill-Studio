"use client";

interface ChannelInfo { channel_id: string; consumer_id: string; channel_type: string; target: string; enabled: boolean; notifications_sent: number; }
interface Props { channels: ChannelInfo[]; appName: string; }

const tIcon: Record<string, string> = { email: "📧", slack: "💬", pagerduty: "🚨", webhook: "🪝", sms: "📱" };

export default function APIDeveloperPlatformSDKWebhookConsumerNotificationChannelCard({ channels, appName }: Props) {
  const activeCount = channels.filter(c => c.enabled).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📢 Notification Channels</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {activeCount}/{channels.length} active</p>
      </div>
      {channels.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No channels</p>
      ) : (
        <div className="space-y-1.5">
          {channels.slice(0, 6).map((c) => (
            <div key={c.channel_id} className={`flex items-center justify-between text-[11px] ${c.enabled ? "" : "opacity-40"}`}>
              <div className="flex items-center gap-1.5">
                <span>{tIcon[c.channel_type] ?? "•"}</span>
                <span className="text-gray-700 dark:text-gray-300">{c.consumer_id}</span>
              </div>
              <span className="text-gray-400">{c.notifications_sent} sent</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
