"use client";

interface ChannelInfo {
  channel_id: string;
  channel_type: string;
  name: string;
  enabled: boolean;
  test_success: boolean | null;
  success_rate: number;
}

interface NotificationChannelCardProps {
  channels: ChannelInfo[];
  appName: string;
}

const typeIcon: Record<string, string> = { email: "📧", slack: "💬", webhook: "🔗", sms: "📱" };

export default function NotificationChannelCard({
  channels,
  appName,
}: NotificationChannelCardProps) {
  const enabled = channels.filter((c) => c.enabled).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🔔 Notification Channels
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {enabled}/{channels.length} enabled
        </span>
      </div>

      {channels.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No channels configured</p>
      ) : (
        <div className="space-y-1.5">
          {channels.map((c) => (
            <div
              key={c.channel_id}
              className={`flex items-center justify-between rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800 ${!c.enabled ? "opacity-50" : ""}`}
            >
              <div className="flex items-center gap-2">
                <span>{typeIcon[c.channel_type] ?? "📨"}</span>
                <span className="text-xs font-medium text-gray-800 dark:text-gray-200">
                  {c.name}
                </span>
                <span className="text-[9px] text-gray-400">{c.channel_type}</span>
              </div>
              <span className="text-[11px] text-gray-400">{c.success_rate}%</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
