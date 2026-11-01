"use client";

interface KeyInfo { key_id: string; name: string; prefix: string; status: string; usage_count: number; }
interface Props { keys: KeyInfo[]; appName: string; }

const sColor: Record<string, string> = { active: "bg-green-100 text-green-700", suspended: "bg-yellow-100 text-yellow-700", revoked: "bg-red-100 text-red-700", expired: "bg-gray-100 text-gray-600" };

export default function APIDeveloperAPIApiDeveloperApiApiKeyLifecycleCard({ keys, appName }: Props) {
  const activeCount = keys.filter(k => k.status === "active").length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔑 Key Lifecycle</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {activeCount}/{keys.length} active</p>
      </div>
      {keys.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No API keys</p>
      ) : (
        <div className="space-y-2">
          {keys.map((k) => (
            <div key={k.key_id} className="flex items-center justify-between rounded-lg bg-gray-50 px-3 py-2 dark:bg-gray-800">
              <div>
                <span className="text-[11px] font-medium text-gray-700 dark:text-gray-300">{k.name}</span>
                <p className="font-mono text-[9px] text-gray-400">{k.prefix}...</p>
              </div>
              <div className="text-right">
                <span className={`rounded-full px-1.5 py-0.5 text-[9px] ${sColor[k.status] ?? ""}`}>{k.status}</span>
                <p className="text-[9px] text-gray-400 mt-0.5">{k.usage_count.toLocaleString()} uses</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
