"use client";

interface ConfigInfo { title: string; version: string; base_url: string; auth_type: string; theme: string; try_it_enabled: boolean; page_views: number; }
interface Props { config: ConfigInfo | null; appName: string; }

export default function APIDeveloperPlatformSDKApiDeveloperApiApiDeveloperApiSwaggerUICard({ config, appName }: Props) {
  if (!config) return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📖 Swagger UI</h3>
      <p className="text-center text-sm text-gray-400 mt-2">Not configured</p>
    </div>
  );
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📖 Swagger UI</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{config.title} v{config.version}</p>
        </div>
        <span className="text-[10px] text-gray-400">{config.page_views.toLocaleString()} views</span>
      </div>
      <div className="space-y-1 text-[11px]">
        <div className="flex justify-between"><span className="text-gray-500">URL</span><span className="text-gray-700 dark:text-gray-300">{config.base_url}</span></div>
        <div className="flex justify-between"><span className="text-gray-500">Auth</span><span className="text-gray-700 dark:text-gray-300">{config.auth_type}</span></div>
        <div className="flex justify-between"><span className="text-gray-500">Theme</span><span className="text-gray-700 dark:text-gray-300">{config.theme}</span></div>
        <div className="flex justify-between"><span className="text-gray-500">Try It</span><span className="text-gray-700 dark:text-gray-300">{config.try_it_enabled ? "✅" : "❌"}</span></div>
      </div>
    </div>
  );
}
