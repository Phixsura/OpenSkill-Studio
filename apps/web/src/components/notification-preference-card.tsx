"use client";

interface NotificationPrefInfo {
  channels: Record<string, boolean>;
  muted_categories: string[];
  global_mute: boolean;
  quiet_hours_start: number | null;
  quiet_hours_end: number | null;
}

interface NotificationPreferenceCardProps {
  pref: NotificationPrefInfo;
  userId: string;
  appName: string;
}

const CHANNEL_ICONS: Record<string, string> = { email: "✉️", push: "📱", in_app: "🔔", sms: "💬" };

export default function NotificationPreferenceCard({
  pref,
  userId,
  appName,
}: NotificationPreferenceCardProps) {
  const enabledChannels = Object.entries(pref.channels).filter(([, v]) => v).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Notifications</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {appName} · {userId}
          </p>
        </div>
        {pref.global_mute ? (
          <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
            🔇 Muted
          </span>
        ) : (
          <span className="text-xs text-gray-400">{enabledChannels} channels on</span>
        )}
      </div>

      {/* Channels */}
      <div className="mb-3 flex flex-wrap gap-2">
        {Object.entries(pref.channels).map(([ch, enabled]) => (
          <span
            key={ch}
            className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[11px] font-medium ${
              enabled
                ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                : "bg-gray-100 text-gray-400 line-through dark:bg-gray-800"
            }`}
          >
            {CHANNEL_ICONS[ch] ?? "📨"} {ch}
          </span>
        ))}
      </div>

      {/* Muted categories */}
      {pref.muted_categories.length > 0 && (
        <div className="mb-2">
          <p className="mb-1 text-[10px] font-medium text-gray-500">Muted categories</p>
          <div className="flex flex-wrap gap-1">
            {pref.muted_categories.map((c) => (
              <span
                key={c}
                className="rounded bg-red-50 px-1.5 py-0.5 text-[10px] text-red-500 dark:bg-red-950/20"
              >
                🔇 {c}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Quiet hours */}
      {pref.quiet_hours_start !== null && pref.quiet_hours_end !== null && (
        <p className="text-[11px] text-gray-400">
          🌙 Quiet hours: {pref.quiet_hours_start}:00 – {pref.quiet_hours_end}:00
        </p>
      )}
    </div>
  );
}
