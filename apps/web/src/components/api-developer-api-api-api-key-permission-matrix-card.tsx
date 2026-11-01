"use client";

interface PermInfo { key_id: string; allowed_count: number; denied_count: number; endpoints: { endpoint: string; methods: string[] }[]; }
interface Props { permissions: PermInfo[]; appName: string; }

export default function APIDeveloperAPIApiApiKeyPermissionMatrixCard({ permissions, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔐 Key Permissions</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {permissions.length} keys</p>
      </div>
      {permissions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No key permissions</p>
      ) : (
        <div className="space-y-2">
          {permissions.map((p) => (
            <div key={p.key_id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-mono font-medium text-gray-700 dark:text-gray-300">{p.key_id}</span>
                <span className="text-gray-400">{p.allowed_count} allowed · {p.denied_count} denied</span>
              </div>
              <div className="mt-1 flex flex-wrap gap-1">
                {p.endpoints.slice(0, 3).map((e) => (
                  <span key={e.endpoint} className="rounded bg-blue-50 px-1 py-0.5 text-[9px] text-blue-700 dark:bg-blue-900 dark:text-blue-200">{e.endpoint} [{e.methods.join(",")}]</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
