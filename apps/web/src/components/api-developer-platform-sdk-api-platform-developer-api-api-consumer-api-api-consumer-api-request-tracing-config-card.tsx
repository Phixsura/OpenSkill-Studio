"use client";

interface ConfigInfo { consumer_id: string; enabled: boolean; sample_rate: number; propagation: string; export_format: string; }
interface Props { configs: ConfigInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestTracingConfigCard({ configs, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔭 Tracing Config</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {configs.length} consumers</p>
      </div>
      {configs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No tracing configs</p>
      ) : (
        <div className="space-y-1">
          {configs.map((c) => (
            <div key={c.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{c.consumer_id}</span>
              <span className="text-gray-400">{(c.sample_rate * 100).toFixed(0)}% · {c.propagation} · {c.export_format}{c.enabled ? "" : " · off"}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
