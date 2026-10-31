"use client";

interface KeyInfo { key_id: string; scopes: string[]; read_only: boolean; description: string; }
interface Props { keys: KeyInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiKeyScopeCard({ keys, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔐 API Key Scopes</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {keys.length} keys</p>
      </div>
      {keys.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No API keys</p>
      ) : (
        <div className="space-y-2">
          {keys.map((k) => (
            <div key={k.key_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="font-mono text-gray-700 dark:text-gray-300">{k.key_id}</span>
                {k.read_only && <span className="rounded bg-blue-100 px-1 text-[9px] text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">READ-ONLY</span>}
              </div>
              <div className="mt-0.5 flex flex-wrap gap-1">
                {k.scopes.map((s) => (
                  <span key={s} className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-600 dark:bg-gray-800 dark:text-gray-400">{s}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
