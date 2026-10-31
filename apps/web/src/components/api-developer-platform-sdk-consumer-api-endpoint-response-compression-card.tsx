"use client";

interface Config { path: string; algorithm: string; minSize: number; level: number; savingsPct: number; compressedCount: number; }
interface Props { configs: Config[]; appName: string; }

export default function APIDeveloperPlatformSDKConsumerApiEndpointResponseCompressionCard({ configs, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🗜️ Response Compression</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {configs.length} endpoints</p>
      </div>
      {configs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No compression configured</p>
      ) : (
        <div className="space-y-2">
          {configs.map((c) => (
            <div key={c.path} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <code className="text-gray-700 dark:text-gray-300">{c.path}</code>
                <span className="rounded bg-blue-100 px-1.5 py-0.5 text-[10px] font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">{c.algorithm}</span>
              </div>
              <div className="mt-0.5 text-[10px] text-gray-400">Min: {c.minSize}B · Level: {c.level} · Savings: {c.savingsPct}% · {c.compressedCount} compressed</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
