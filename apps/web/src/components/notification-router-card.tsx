"use client";

interface ChannelInfo {
  channel_id: string;
  channel_type: "webhook" | "email" | "slack" | "in_app";
  target: string;
  event_types: string[] | null;
  enabled: boolean;
  delivery_count: number;
  last_delivery_status: "delivered" | "failed" | "skipped" | null;
}

interface NotificationRouterCardProps {
  channels: ChannelInfo[];
  appName: string;
}

const CHANNEL_ICONS: Record<string, string> = {
  webhook: "🔗",
  email: "✉️",
  slack: "💬",
  in_app: "🔔",
};

const CHANNEL_LABELS: Record<string, string> = {
  webhook: "Webhook",
  email: "Email",
  slack: "Slack",
  in_app: "In-App",
};

const STATUS_STYLES: Record<string, { dot: string; label: string }> = {
  delivered: { dot: "bg-green-500", label: "Delivered" },
  failed: { dot: "bg-red-500", label: "Failed" },
  skipped: { dot: "bg-gray-400", label: "Skipped" },
};

export default function NotificationRouterCard({ channels, appName }: NotificationRouterCardProps) {
  const activeCount = channels.filter((c) => c.enabled).length;
  const disabledCount = channels.filter((c) => !c.enabled).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      {/* Header */}
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Notification Channels
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex gap-2">
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
            {activeCount} active
          </span>
          {disabledCount > 0 && (
            <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600 dark:bg-gray-800 dark:text-gray-400">
              {disabledCount} disabled
            </span>
          )}
        </div>
      </div>

      {/* Channel list */}
      {channels.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No channels configured</p>
      ) : (
        <div className="space-y-3">
          {channels.map((ch) => (
            <div
              key={ch.channel_id}
              className={`rounded-lg border p-3 ${
                ch.enabled
                  ? "border-gray-100 dark:border-gray-800"
                  : "border-gray-100 bg-gray-50 opacity-60 dark:border-gray-800 dark:bg-gray-800/50"
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span>{CHANNEL_ICONS[ch.channel_type] ?? "📨"}</span>
                  <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
                    {CHANNEL_LABELS[ch.channel_type] ?? ch.channel_type}
                  </span>
                  {!ch.enabled && <span className="text-[10px] text-gray-400">disabled</span>}
                </div>
                {ch.last_delivery_status && (
                  <div className="flex items-center gap-1">
                    <span
                      className={`h-1.5 w-1.5 rounded-full ${
                        STATUS_STYLES[ch.last_delivery_status]?.dot ?? "bg-gray-400"
                      }`}
                    />
                    <span className="text-[11px] text-gray-500">
                      {STATUS_STYLES[ch.last_delivery_status]?.label}
                    </span>
                  </div>
                )}
              </div>
              <p className="mt-1 truncate font-mono text-xs text-gray-500 dark:text-gray-400">
                {ch.target}
              </p>
              <div className="mt-1.5 flex items-center justify-between">
                <span className="text-[11px] text-gray-400">
                  {ch.event_types
                    ? `${ch.event_types.length} event type${ch.event_types.length !== 1 ? "s" : ""}`
                    : "All events"}
                </span>
                <span className="text-[11px] text-gray-400">{ch.delivery_count} deliveries</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
