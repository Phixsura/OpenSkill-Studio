"use client";

interface Channel { type: string; target: string; enabled: boolean; }
interface Props { consumerId: string; channels: Channel[]; mutedCategories: string[]; digestMode: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerNotificationPreferenceCard({ consumerId, channels, mutedCategories, digestMode, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔔 Notification Preferences</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {digestMode}</p>
      </div>
      <div className="mb-3 space-y-1">
        {channels.map((ch, i) => (
          <div key={i} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[11px] dark:bg-gray-800">
            <span className="text-gray-700 dark:text-gray-300">{ch.type}: {ch.target}</span>
            <span className={ch.enabled ? "text-green-500" : "text-gray-400"}>{ch.enabled ? "ON" : "OFF"}</span>
          </div>
        ))}
        {channels.length === 0 && <p className="text-center text-sm text-gray-400">No channels</p>}
      </div>
      {mutedCategories.length > 0 && (
        <div className="flex flex-wrap gap-1">
          <span className="text-[10px] text-gray-400">Muted:</span>
          {mutedCategories.map((c) => (
            <span key={c} className="rounded bg-gray-200 px-1.5 py-0.5 text-[10px] text-gray-500 dark:bg-gray-700">{c}</span>
          ))}
        </div>
      )}
    </div>
  );
}
