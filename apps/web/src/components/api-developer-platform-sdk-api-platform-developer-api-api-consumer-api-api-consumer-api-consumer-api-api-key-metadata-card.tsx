"use client";

interface Key { id: string; label: string; environment: string; requestCount: number; lastUsed: string | null; tags: Record<string, string>; }
interface Props { keys: Key[]; consumerId: string; appName: string; }

const envColors: Record<string, string> = {
  production: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  staging: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  development: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiKeyMetadataCard({ keys, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔑 API Key Metadata</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {keys.length} keys</p>
      </div>
      {keys.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No API keys</p>
      ) : (
        <div className="space-y-2">
          {keys.map((k) => (
            <div key={k.id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{k.label || k.id}</span>
                <span className={`rounded px-1.5 py-0.5 text-[9px] font-medium ${envColors[k.environment] ?? ""}`}>{k.environment}</span>
              </div>
              <div className="mt-0.5 text-[10px] text-gray-400">{k.requestCount.toLocaleString()} requests{k.lastUsed && ` · Last: ${k.lastUsed}`}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
