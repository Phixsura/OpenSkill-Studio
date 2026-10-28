"use client";

interface PrefInfo {
  user_id: string;
  channels: string[];
  muted_count: number;
  has_quiet_hours: boolean;
}

interface APINotificationPreferenceCardProps {
  preferences: PrefInfo[];
  appName: string;
}

export default function APINotificationPreferenceCard({ preferences, appName }: APINotificationPreferenceCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔕 Notification Prefs</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{preferences.length} users</span>
      </div>

      {preferences.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No custom preferences</p>
      ) : (
        <div className="space-y-1.5">
          {preferences.map((p) => (
            <div key={p.user_id} className="rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800">
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-700 dark:text-gray-300">{p.user_id}</span>
                {p.has_quiet_hours && <span className="text-[9px] text-gray-400">🌙 quiet hours</span>}
              </div>
              <div className="mt-0.5 flex gap-1">
                {p.channels.map((c) => (
                  <span key={c} className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">{c}</span>
                ))}
                {p.muted_count > 0 && <span className="text-[9px] text-orange-500">{p.muted_count} muted</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
