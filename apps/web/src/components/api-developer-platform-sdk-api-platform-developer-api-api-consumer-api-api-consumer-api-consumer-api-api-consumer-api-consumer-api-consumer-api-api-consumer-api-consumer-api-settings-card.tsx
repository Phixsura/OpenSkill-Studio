"use client";

interface SettingItem { key: string; value: string; category: string; isSecret: boolean; }
interface Props { settings: SettingItem[]; categories: string[]; consumerId: string; appName: string; }

const catColors: Record<string, string> = {
  security: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  billing: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  api: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  notifications: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiSettingsCard({ settings, categories, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚙️ Consumer Settings</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {categories.length} categories</p>
      </div>
      {settings.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No settings</p>
      ) : (
        <div className="space-y-1">
          {settings.map((s) => (
            <div key={s.key} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[10px] dark:bg-gray-800">
              <div className="flex items-center gap-1">
                <span className={`rounded px-1 py-0.5 text-[8px] ${catColors[s.category] ?? "bg-gray-200 text-gray-600"}`}>{s.category}</span>
                <code className="text-gray-700 dark:text-gray-300">{s.key}</code>
              </div>
              <span className={s.isSecret ? "italic text-gray-400" : "text-gray-500"}>{s.value}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
