"use client";

interface ConfigInfo { consumer_id: string; mirror_url: string; sample_rate: number; enabled: boolean; }
interface Props { configs: ConfigInfo[]; mirrored: number; failed: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestMirrorCard({ configs, mirrored, failed, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🪞 Request Mirror</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-[10px] text-gray-400">{mirrored.toLocaleString()} mirrored · {failed} failed</span>
      </div>
      {configs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No mirror configs</p>
      ) : (
        <div className="space-y-1">
          {configs.map((c) => (
            <div key={c.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{c.consumer_id}</span>
              <span className={c.enabled ? "text-green-600 dark:text-green-400" : "text-gray-400"}>{(c.sample_rate * 100).toFixed(0)}% · {c.enabled ? "on" : "off"}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
