"use client";

interface KeyInfo { keyId: string; scopes: string[]; denyScopes: string[]; }
interface Props { keys: KeyInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiKeyScopeManagerCard({ keys, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔐 Key Scopes</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {keys.length} keys</p>
      </div>
      {keys.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No keys configured</p>
      ) : (
        <div className="space-y-2">
          {keys.map((k) => (
            <div key={k.keyId} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="text-[11px] font-medium text-gray-700 dark:text-gray-300">{k.keyId}</div>
              <div className="mt-1 flex flex-wrap gap-1">
                {k.scopes.map((s) => (
                  <span key={s} className="rounded bg-green-100 px-1.5 py-0.5 text-[10px] text-green-700 dark:bg-green-900/30 dark:text-green-400">{s}</span>
                ))}
                {k.denyScopes.map((s) => (
                  <span key={s} className="rounded bg-red-100 px-1.5 py-0.5 text-[10px] text-red-700 line-through dark:bg-red-900/30 dark:text-red-400">{s}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
