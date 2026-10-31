"use client";

interface PermInfo { endpoint: string; method: string; allowed: boolean; }
interface MatrixInfo { key_id: string; consumer_id: string; permissions: PermInfo[]; default_allow: boolean; }
interface Props { matrices: MatrixInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiKeyPermissionMatrixCard({ matrices, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔐 Key Permissions</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {matrices.length} keys</p>
      </div>
      {matrices.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No permission matrices</p>
      ) : (
        <div className="space-y-2">
          {matrices.map((m) => (
            <div key={m.key_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="font-mono text-gray-700 dark:text-gray-300">{m.key_id}</span>
                <span className="text-[9px] text-gray-400">{m.default_allow ? "allow" : "deny"} default</span>
              </div>
              <div className="mt-0.5 flex flex-wrap gap-1">
                {m.permissions.map((p, i) => (
                  <span key={i} className={`rounded px-1 text-[9px] ${p.allowed ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400" : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"}`}>{p.method} {p.endpoint}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
