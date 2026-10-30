"use client";

interface Rule { id: string; path: string; consumerId: string; action: string; reason: string; }
interface Props { rules: Rule[]; defaultPolicy: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointAccessControlListCard({ rules, defaultPolicy, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🛡️ Access Control</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — Default: {defaultPolicy} · {rules.length} rules</p>
      </div>
      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No ACL rules</p>
      ) : (
        <div className="space-y-1">
          {rules.map((r) => (
            <div key={r.id} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[10px] dark:bg-gray-800">
              <div>
                <code className="text-gray-600 dark:text-gray-400">{r.path}</code>
                <span className="ml-1 text-gray-400">→ {r.consumerId}</span>
              </div>
              <span className={`rounded px-1.5 py-0.5 font-medium ${r.action === "allow" ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400" : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"}`}>{r.action}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
