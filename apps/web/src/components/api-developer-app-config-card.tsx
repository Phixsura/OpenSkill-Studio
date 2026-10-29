"use client";

interface AppInfo { app_id: string; name: string; setting_count: number; flag_count: number; }
interface Props { apps: AppInfo[]; appName: string; }

export default function APIDeveloperAppConfigCard({ apps, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚙️ App Configs</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{apps.length} apps</span>
      </div>
      {apps.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No app configs</p>
      ) : (
        <div className="space-y-1">
          {apps.map((a) => (
            <div key={a.app_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{a.name}</span>
              <span className="text-gray-400">{a.setting_count} settings · {a.flag_count} flags</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
