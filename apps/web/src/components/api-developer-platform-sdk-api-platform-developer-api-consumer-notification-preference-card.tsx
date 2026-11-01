"use client";

interface PrefInfo { consumer_id: string; email: boolean; slack: boolean; webhook: boolean; frequency: string; quiet_hours: string; }
interface Props { preferences: PrefInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerNotificationPreferenceCard({ preferences, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔔 Notification Prefs</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {preferences.length} consumers</p>
      </div>
      {preferences.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No preferences set</p>
      ) : (
        <div className="space-y-1.5">
          {preferences.map((p) => (
            <div key={p.consumer_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{p.consumer_id}</span>
                <span className="text-gray-400">{p.frequency}</span>
              </div>
              <div className="flex gap-2 text-[10px] text-gray-400">
                {p.email && <span>📧</span>}{p.slack && <span>💬</span>}{p.webhook && <span>🔗</span>}
                {p.quiet_hours !== "none" && <span>🌙 {p.quiet_hours}</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
